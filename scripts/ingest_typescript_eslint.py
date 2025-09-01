\
#!/usr/bin/env python3
import os, re, json, pathlib
from utils.common import ensure_dirs, VENDOR_DIR, NORM_DIR, canon_record

OUT = NORM_DIR / "typescript-eslint.jsonl"

def find_rules_dir():
    candidates = [
        VENDOR_DIR / "typescript-eslint" / "packages" / "eslint-plugin" / "docs" / "rules",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def parse_rule_md(path: pathlib.Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'^\s*#\s+(.+?)\s*$', text, flags=re.MULTILINE)
    title = m.group(1).strip() if m else path.stem
    paras = re.split(r'\n\s*\n', text.strip(), maxsplit=4)
    desc = paras[1].strip() if len(paras) > 1 else ""
    rule_id = path.stem
    return rule_id, title, desc

if __name__ == "__main__":
    ensure_dirs()
    rules_dir = find_rules_dir()
    if not rules_dir:
        print("WARN: typescript-eslint repo not present; run fetch-repos.")
        open(OUT, "w").close()
        raise SystemExit(0)
    recs = []
    for p in rules_dir.glob("*.md"):
        rid, title, desc = parse_rule_md(p)
        recs.append(canon_record(
            source="typescript-eslint",
            language=["ts"],
            rule_id=rid,
            name=title,
            summary=desc[:180],
            description_md=desc,
            category="code_smell",
            severity="major",
            tags=["typescript-eslint","eslint"],
            mappings={},
            links={"doc": f"https://typescript-eslint.io/rules/{rid}"},
            meta={"ingest_source":"md","file":str(p)}
        ))
    with open(OUT, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"typescript-eslint.jsonl written: {len(recs)} rules.")
