\
#!/usr/bin/env python3
import os, re, json, pathlib
from utils.common import ensure_dirs, VENDOR_DIR, NORM_DIR, canon_record

OUT = NORM_DIR / "ruff.jsonl"

def rules_dir():
    # Ruff docs include one file per rule under docs/rules
    candidates = [
        VENDOR_DIR / "ruff" / "docs" / "rules",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def parse_rule_md(path: pathlib.Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    title = None
    m = re.search(r'^\s*#\s+(.+?)\s*$', text, flags=re.MULTILINE)
    if m: title = m.group(1).strip()
    code = path.stem.upper()
    desc = ""
    paras = re.split(r'\n\s*\n', text.strip(), maxsplit=4)
    if len(paras) > 1:
        desc = paras[1].strip()
    return code, title or code, desc

if __name__ == "__main__":
    ensure_dirs()
    d = rules_dir()
    if not d:
        print("WARN: ruff repo not present; run fetch-repos.")
        open(OUT, "w").close()
        raise SystemExit(0)
    recs = []
    for p in sorted(d.glob("*.md")):
        code, title, desc = parse_rule_md(p)
        recs.append(canon_record(
            source="ruff",
            language="py",
            rule_id=code,
            name=title,
            summary=desc[:180],
            description_md=desc,
            category="code_smell",
            severity="major",
            tags=["ruff"],
            mappings={},
            links={"doc": f"https://docs.astral.sh/ruff/rules/{code.lower()}/"},
            meta={"ingest_source":"md","file":str(p)}
        ))
    with open(OUT, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"ruff.jsonl written: {len(recs)} rules.")
