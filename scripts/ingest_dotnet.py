\
#!/usr/bin/env python3
import os, re, json, pathlib
from utils.common import ensure_dirs, VENDOR_DIR, NORM_DIR, canon_record

OUT = NORM_DIR / "dotnet.jsonl"

def rules_dir():
    # .NET docs have rule pages under this path
    return VENDOR_DIR / "dotnet-docs" / "docs" / "fundamentals" / "code-analysis" / "quality-rules"

def parse_rule_md(path: pathlib.Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Try to capture front-matter title or first heading
    m = re.search(r'^\s*#\s+(.+?)\s*$', text, flags=re.MULTILINE)
    title = m.group(1).strip() if m else path.stem.upper()
    # First paragraph as summary
    paras = re.split(r'\n\s*\n', text.strip(), maxsplit=4)
    desc = paras[1].strip() if len(paras) > 1 else ""
    rule_id = path.stem.upper()  # e.g., CAXXXX
    return rule_id, title, desc

if __name__ == "__main__":
    ensure_dirs()
    d = rules_dir()
    if not d.exists():
        print("WARN: dotnet docs repo not present; run fetch-repos.")
        open(OUT, "w").close()
        raise SystemExit(0)
    recs = []
    for p in d.glob("ca*.md"):
        rid, title, desc = parse_rule_md(p)
        recs.append(canon_record(
            source=".net",
            language=["cs","vb"],
            rule_id=rid,
            name=title,
            summary=desc[:180],
            description_md=desc,
            category="code_smell",
            severity="major",
            tags=["dotnet","roslyn-analyzers"],
            mappings={},
            links={"doc": f"https://learn.microsoft.com/dotnet/fundamentals/code-analysis/quality-rules/{rid.lower()}"},
            meta={"ingest_source":"md","file":str(p)}
        ))
    with open(OUT,"w",encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"dotnet.jsonl written: {len(recs)} rules.")
