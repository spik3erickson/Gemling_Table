"""Build normalized PoE2 passive-tree datasets from GGG's official export.

Source: https://github.com/grindinggear/poe2-skilltree-export (data.json, ~5MB).
The export has 5,151 nodes; we extract the player-allocatable NOTABLES and
KEYSTONES (excluding ascendancy nodes) with their stat lines, so the optimizer
can recommend real notables for amulet anointments and for spending remaining
passive points. The export carries no "anointable" flag, so every non-ascendancy
notable is treated as an anoint candidate (the common case in PoE2 0.5).

Usage:  python3 scripts/build_tree.py
"""

import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).parent.parent
RAW = HERE / "data" / "_raw" / "tree.json"
SRC_URL = "https://raw.githubusercontent.com/grindinggear/poe2-skilltree-export/main/data.json"
OUT_NOTABLES = HERE / "data" / "tree_notables.json"
OUT_KEYSTONES = HERE / "data" / "tree_keystones.json"


def clean(stats: list) -> list[str]:
    out = []
    for s in stats or []:
        s = re.sub(r"<[^>]+>", "", str(s))          # strip <underline>{...} markup
        s = s.replace("{", "").replace("}", "")
        s = re.sub(r"\[([^\[\]|]+)\|([^\[\]]+)\]", r"\2", s)  # [Key|Display] -> Display
        s = re.sub(r"\[([^\[\]]+)\]", r"\1", s)               # [Display] -> Display
        s = re.sub(r"\s+", " ", s.replace("\n", " · ")).strip()
        if s:
            out.append(s)
    return out


def main() -> None:
    if not RAW.exists():
        RAW.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-s", SRC_URL, "-o", str(RAW)], check=True)
    data = json.loads(RAW.read_text(encoding="utf-8"))
    nodes = data.get("nodes", {})

    notables, keystones = {}, {}
    for n in nodes.values():
        if not isinstance(n, dict) or n.get("ascendancyId"):   # skip ascendancy nodes
            continue
        name, stats = n.get("name"), clean(n.get("stats"))
        if not name or not stats:
            continue
        if n.get("isKeystone"):
            keystones.setdefault(name, {"name": name, "stats": stats})
        elif n.get("isNotable") and not n.get("grantedSkill"):  # skip skill-granting notables
            notables.setdefault(name, {"name": name, "stats": stats})

    nl = sorted(notables.values(), key=lambda x: x["name"].lower())
    kl = sorted(keystones.values(), key=lambda x: x["name"].lower())
    OUT_NOTABLES.write_text(json.dumps(
        {"version": "0.5", "source": "grindinggear/poe2-skilltree-export",
         "note": "Non-ascendancy notables (stat-bearing, non-skill-granting). Anoint candidates + tree-routing pool.",
         "count": len(nl), "notables": nl}, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_KEYSTONES.write_text(json.dumps(
        {"version": "0.5", "source": "grindinggear/poe2-skilltree-export",
         "count": len(kl), "keystones": kl}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"notables={len(nl)} keystones={len(kl)} -> {OUT_NOTABLES.name}, {OUT_KEYSTONES.name}")


if __name__ == "__main__":
    main()
