#!/usr/bin/env python3
"""
build_compat_validation.py — validate and enrich PoE2 v0.5 support-gem
compatibility matrix against poe2db.tw authoritative "Supported By" data.

Usage:
    python3 scripts/build_compat_validation.py [--skip-download]

Outputs (all in data/):
    poe2db_supportedby.json          raw scrape results per skill
    support_compatibility_pob.json   prior PoB-computed matrix (backup)
    support_compatibility.json       replaced with poe2db authoritative data
    compat_validation.md             disagreement report
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise SystemExit("beautifulsoup4 required: pip install beautifulsoup4")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "_raw" / "supportedby"

SKILL_GEMS_FILE = DATA_DIR / "skill_gems.json"
SUPPORT_GEMS_FILE = DATA_DIR / "support_gems.json"
COMPAT_FILE = DATA_DIR / "support_compatibility.json"
COMPAT_POB_FILE = DATA_DIR / "support_compatibility_pob.json"
SUPPORTEDBY_FILE = DATA_DIR / "poe2db_supportedby.json"
GEMLING_QUALITY_FILE = DATA_DIR / "gemling_quality.json"
VALIDATION_FILE = DATA_DIR / "compat_validation.md"

BASE_URL = "https://poe2db.tw/us"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)
CONCURRENCY = 4
DELAY_PER_WORKER = 0.25  # seconds between requests per worker slot


# ---------------------------------------------------------------------------
# Slug derivation
# ---------------------------------------------------------------------------

def derive_slug(name: str) -> str:
    """Derive poe2db slug from a skill gem name."""
    s = name.replace("'", "").replace(" ", "_")
    return s


def slug_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


# ---------------------------------------------------------------------------
# Per-skill slug map: prefer gemling_quality.json entries
# ---------------------------------------------------------------------------

def build_slug_map(skill_names: list[str]) -> dict[str, str]:
    slug_map: dict[str, str] = {}
    try:
        with open(GEMLING_QUALITY_FILE) as fh:
            gq = json.load(fh)
        for entry in gq.get("skills", []):
            name = entry.get("name", "")
            url = entry.get("url", "")
            if name and url:
                slug_map[name] = slug_from_url(url)
    except OSError:
        pass

    for name in skill_names:
        if name not in slug_map:
            slug_map[name] = derive_slug(name)

    return slug_map


# ---------------------------------------------------------------------------
# HTTP fetch with caching
# ---------------------------------------------------------------------------

def fetch_page(slug: str, skip_download: bool) -> Optional[str]:
    cache_path = RAW_DIR / f"{slug}.html"
    if cache_path.exists():
        try:
            return cache_path.read_text(encoding="utf-8")
        except OSError:
            pass

    if skip_download:
        return None

    url = f"{BASE_URL}/{slug}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    except OSError as exc:
        raise RuntimeError(f"fetch failed for {url}: {exc}") from exc

    try:
        cache_path.write_text(html, encoding="utf-8")
    except OSError:
        pass

    return html


# ---------------------------------------------------------------------------
# Parse "Supported By" section
# ---------------------------------------------------------------------------

@dataclass
class ParseResult:
    skill_name: str
    slug: str
    expected_count: Optional[int]
    supports: list[str]
    error: Optional[str] = None


def parse_supported_by(html: str, skill_name: str, slug: str) -> ParseResult:
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find(id="SupportedBy")
    if container is None:
        return ParseResult(skill_name, slug, None, [], error="no #SupportedBy element")

    # Tab label: "Supported By /N" — grab expected count
    expected_count: Optional[int] = None
    tab_link = soup.find("a", href="#SupportedBy")
    if tab_link is None:
        # Also try by text containing "Supported By"
        for a in soup.find_all("a"):
            if "SupportedBy" in (a.get("href") or ""):
                tab_link = a
                break
    if tab_link:
        tab_text = tab_link.get_text(strip=True)
        m = re.search(r"/(\d+)", tab_text)
        if m:
            expected_count = int(m.group(1))

    # Anchors inside #SupportedBy that link into /us/ and contain no <img>
    anchors = container.select('a[href^="/us/"]')
    names: list[str] = []
    seen: set[str] = set()
    for a in anchors:
        if a.find("img"):
            continue
        text = a.get_text(strip=True)
        if text and text not in seen:
            seen.add(text)
            names.append(text)

    error: Optional[str] = None
    if expected_count is not None and len(names) != expected_count:
        error = f"count mismatch: expected {expected_count}, got {len(names)}"

    return ParseResult(skill_name, slug, expected_count, names, error=error)


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

def process_skill(
    skill_name: str,
    slug: str,
    skip_download: bool,
) -> ParseResult:
    time.sleep(DELAY_PER_WORKER)
    try:
        html = fetch_page(slug, skip_download)
    except RuntimeError as exc:
        return ParseResult(skill_name, slug, None, [], error=str(exc))

    if html is None:
        return ParseResult(skill_name, slug, None, [], error="404 or no cache")

    return parse_supported_by(html, skill_name, slug)


# ---------------------------------------------------------------------------
# Main scrape
# ---------------------------------------------------------------------------

def run_scrape(
    skill_names: list[str],
    slug_map: dict[str, str],
    skip_download: bool,
) -> dict[str, ParseResult]:
    results: dict[str, ParseResult] = {}
    tasks = [(name, slug_map[name]) for name in skill_names]

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = {
            pool.submit(process_skill, name, slug, skip_download): name
            for name, slug in tasks
        }
        done = 0
        total = len(futures)
        for fut in as_completed(futures):
            name = futures[fut]
            done += 1
            try:
                result = fut.result()
            except Exception as exc:
                result = ParseResult(name, slug_map[name], None, [], error=str(exc))
            results[name] = result
            if done % 50 == 0 or done == total:
                print(f"  {done}/{total} skills processed", flush=True)

    return results


# ---------------------------------------------------------------------------
# Build output files
# ---------------------------------------------------------------------------

def build_supportedby_json(
    results: dict[str, ParseResult],
    skill_names: list[str],
) -> dict:
    skills_out: dict[str, dict] = {}
    errors: list[dict] = []

    for name in skill_names:
        r = results[name]
        if r.error and not r.supports:
            errors.append({"skill": name, "slug": r.slug, "error": r.error})
        else:
            entry: dict = {
                "expected_count": r.expected_count,
                "supports": r.supports,
            }
            if r.error:
                entry["warning"] = r.error
            skills_out[name] = entry

    return {
        "version": "0.5",
        "source": "poe2db.tw /us/<gem>#SupportedBy",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "skills": skills_out,
        "errors": errors,
    }


def build_new_compat(
    results: dict[str, ParseResult],
    pob_compat: dict,
    known_support_names: set[str],
) -> tuple[dict, list[str], list[str]]:
    """
    Returns (new_compat_dict, fallback_skills, unmatched_supports).
    fallback_skills: skills that used PoB data because scrape failed.
    unmatched_supports: poe2db support names not in support_gems.json.
    """
    by_skill: dict[str, list[str]] = {}
    fallback_skills: list[str] = []
    unmatched_set: dict[str, list[str]] = {}  # support_name -> [skills]

    pob_by_skill = pob_compat.get("by_skill", {})

    for name, r in results.items():
        if r.error and not r.supports:
            # Fall back to PoB-computed
            if name in pob_by_skill:
                by_skill[name] = pob_by_skill[name]
                fallback_skills.append(name)
            # else omit (was not in PoB either)
        else:
            filtered: list[str] = []
            for sup in r.supports:
                if sup in known_support_names:
                    filtered.append(sup)
                else:
                    if sup not in unmatched_set:
                        unmatched_set[sup] = []
                    if name not in unmatched_set[sup]:
                        unmatched_set[sup].append(name)
            by_skill[name] = filtered

    # Build by_support (reverse index)
    by_support: dict[str, list[str]] = {}
    for skill, supports in by_skill.items():
        for sup in supports:
            by_support.setdefault(sup, []).append(skill)

    # Sort for determinism
    for lst in by_skill.values():
        lst.sort()
    for lst in by_support.values():
        lst.sort()

    new_compat = {"by_support": by_support, "by_skill": by_skill}
    unmatched_list = sorted(unmatched_set.keys())

    return new_compat, fallback_skills, unmatched_set


# ---------------------------------------------------------------------------
# Validation report
# ---------------------------------------------------------------------------

def build_validation_report(
    results: dict[str, ParseResult],
    pob_compat: dict,
    new_compat: dict,
    fallback_skills: list[str],
    unmatched_set: dict[str, list[str]],
) -> str:
    pob_by_skill = pob_compat.get("by_skill", {})
    new_by_skill = new_compat["by_skill"]

    total_skills = len(results)
    errored_skills = [r for r in results.values() if r.error and not r.supports]
    scraped_ok = total_skills - len(errored_skills)

    # Agreement analysis: only over skills present in both matrices
    agree = 0
    poe2db_only = 0
    pob_only = 0
    per_skill_disagree: list[tuple[int, str]] = []  # (disagreement_count, name)

    all_skill_names = set(new_by_skill) | set(pob_by_skill)
    for name in all_skill_names:
        new_set = set(new_by_skill.get(name, []))
        pob_set = set(pob_by_skill.get(name, []))
        a = len(new_set & pob_set)
        p2 = len(new_set - pob_set)
        pb = len(pob_set - new_set)
        agree += a
        poe2db_only += p2
        pob_only += pb
        disagree_count = p2 + pb
        if disagree_count > 0:
            per_skill_disagree.append((disagree_count, name))

    total_pairs = agree + poe2db_only + pob_only
    per_skill_disagree.sort(reverse=True)
    top15 = per_skill_disagree[:15]

    lines: list[str] = [
        "# PoE2 v0.5 Support Compatibility Validation",
        f"_Generated: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## Scrape Summary",
        f"- Skills in catalog: {total_skills}",
        f"- Successfully scraped: {scraped_ok}",
        f"- Errors (fell back to PoB): {len(errored_skills)}",
        f"- Fallback skills: {len(fallback_skills)}",
        "",
        "## Agreement: poe2db vs PoB-computed",
        f"- Total (skill,support) pairs evaluated: {total_pairs}",
        f"- Agree: {agree} ({agree*100//total_pairs if total_pairs else 0}%)",
        f"- poe2db-only (new compat found): {poe2db_only}",
        f"- PoB-only (PoB had it, poe2db does not): {pob_only}",
        "",
        "## Top 15 Skills by Disagreement",
        "",
        "| Skill | poe2db count | PoB count | Disagree delta |",
        "|-------|-------------|-----------|----------------|",
    ]

    for delta, name in top15:
        p2c = len(new_by_skill.get(name, []))
        pbc = len(pob_by_skill.get(name, []))
        lines.append(f"| {name} | {p2c} | {pbc} | {delta} |")

    lines += [
        "",
        "## Spot-check: Enervating Nova",
    ]
    en_poe2db = new_by_skill.get("Enervating Nova", [])
    en_pob = pob_by_skill.get("Enervating Nova", [])
    lines.append(f"- poe2db count: {len(en_poe2db)}")
    lines.append(f"- PoB count: {len(en_pob)}")
    bl_present = "Bloodlust" in en_poe2db
    lines.append(f"- Bloodlust absent (expected): {'YES (correct)' if not bl_present else 'NO (unexpected - check)'}")
    # Check a generic spell support is present
    ambrosia_present = any("Ambrosia" in s for s in en_poe2db)
    lines.append(f"- Generic spell support (Ambrosia) present: {'YES' if ambrosia_present else 'NO'}")

    lines += [
        "",
        f"## Unmatched Support Names ({len(unmatched_set)} unique)",
        "_These support names appear on poe2db but are NOT in support_gems.json._",
        "_Likely unique-item-granted or league-mechanic supports not yet catalogued._",
        "",
        "| Support Name | Skills referencing it |",
        "|-------------|----------------------|",
    ]

    for sup_name in sorted(unmatched_set.keys()):
        skill_refs = unmatched_set[sup_name]
        skill_str = ", ".join(skill_refs[:5])
        if len(skill_refs) > 5:
            skill_str += f" (+{len(skill_refs)-5} more)"
        lines.append(f"| {sup_name} | {skill_str} |")

    lines += [
        "",
        "## Errors",
        "",
    ]
    for r in errored_skills:
        lines.append(f"- **{r.skill_name}** (`{r.slug}`): {r.error}")

    if fallback_skills:
        lines += [
            "",
            "## Fallback Skills (using PoB data)",
            "",
        ]
        for name in sorted(fallback_skills):
            lines.append(f"- {name}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build poe2db support compat validation")
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Use only cached HTML pages; do not fetch from poe2db.tw",
    )
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Load skill list
    with open(SKILL_GEMS_FILE) as fh:
        skill_gems: list[dict] = json.load(fh)
    skill_names = [g["name"] for g in skill_gems]
    print(f"Loaded {len(skill_names)} skill gems")

    # Load support names
    with open(SUPPORT_GEMS_FILE) as fh:
        support_gems: list[dict] = json.load(fh)
    known_support_names: set[str] = {g["name"] for g in support_gems}
    print(f"Loaded {len(known_support_names)} support gems")

    # Load existing PoB compat (before overwriting)
    with open(COMPAT_FILE) as fh:
        pob_compat: dict = json.load(fh)
    print(f"Loaded PoB compat: {len(pob_compat.get('by_skill',{}))} skills")

    # Back up PoB compat
    with open(COMPAT_POB_FILE, "w") as fh:
        json.dump(pob_compat, fh, separators=(",", ":"))
    print(f"Backed up PoB compat to {COMPAT_POB_FILE.name}")

    # Build slug map
    slug_map = build_slug_map(skill_names)

    # Scrape
    print(f"Scraping {len(skill_names)} skills (concurrency={CONCURRENCY})...")
    results = run_scrape(skill_names, slug_map, args.skip_download)

    # Build poe2db_supportedby.json
    supportedby_data = build_supportedby_json(results, skill_names)
    with open(SUPPORTEDBY_FILE, "w") as fh:
        json.dump(supportedby_data, fh, indent=2)
    print(f"Wrote {SUPPORTEDBY_FILE.name} ({SUPPORTEDBY_FILE.stat().st_size:,} bytes)")

    # Build new compat matrix
    new_compat, fallback_skills, unmatched_set = build_new_compat(
        results, pob_compat, known_support_names
    )
    with open(COMPAT_FILE, "w") as fh:
        json.dump(new_compat, fh, separators=(",", ":"))
    print(f"Wrote {COMPAT_FILE.name} ({COMPAT_FILE.stat().st_size:,} bytes)")

    # Validation report
    report = build_validation_report(
        results, pob_compat, new_compat, fallback_skills, unmatched_set
    )
    VALIDATION_FILE.write_text(report, encoding="utf-8")
    print(f"Wrote {VALIDATION_FILE.name} ({VALIDATION_FILE.stat().st_size:,} bytes)")

    # Terminal summary
    errored = supportedby_data["errors"]
    scraped_ok = len(supportedby_data["skills"])
    print()
    print(f"=== DONE ===")
    print(f"Skills scraped OK : {scraped_ok}/{len(skill_names)}")
    print(f"Errors            : {len(errored)}")
    print(f"Fallback (PoB)    : {len(fallback_skills)}")
    print(f"Unmatched supports: {len(unmatched_set)}")

    en = new_compat['by_skill'].get('Enervating Nova', [])
    print(f"Enervating Nova   : {len(en)} supports (poe2db)")
    pob_en = pob_compat.get('by_skill', {}).get('Enervating Nova', [])
    print(f"Enervating Nova   : {len(pob_en)} supports (PoB)")

    files = [SUPPORTEDBY_FILE, COMPAT_POB_FILE, COMPAT_FILE, VALIDATION_FILE]
    print()
    print("Files written:")
    for f in files:
        try:
            print(f"  {f.relative_to(REPO_ROOT)}  ({f.stat().st_size:,} bytes)")
        except OSError:
            print(f"  {f.name}  (missing)")


if __name__ == "__main__":
    main()
