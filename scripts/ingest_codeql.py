\
#!/usr/bin/env python3
import os, re, json, pathlib
from utils.common import ensure_dirs, VENDOR_DIR, NORM_DIR, canon_record

OUT = NORM_DIR / "codeql.jsonl"
META_RE = re.compile(r'@(?P<k>id|name|description|kind|tags|precision)\s+(?P<v>.+)')

LANG_DIRS = ["cpp","csharp","go","java","javascript","python","ruby","swift","kotlin"]

def scan_queries(root: pathlib.Path):
    for lang in LANG_DIRS:
        base = root / lang / "ql" / "src"
        if not base.exists(): 
            continue
        for ql in base.rglob("*.ql"):
            yield lang, ql

def parse_metadata(text):
    # Look for block comments with @id @name etc.
    meta = {}
    for m in META_RE.finditer(text):
        k, v = m.group("k"), m.group("v").strip()
        if k == "tags":
            meta[k] = [t.strip() for t in re.split(r'[,\s]+', v) if t.strip()]
        else:
            meta[k] = v
    return meta

if __name__ == "__main__":
    ensure_dirs()
    root = VENDOR_DIR / "codeql"
    if not root.exists():
        print("WARN: codeql repo not present; run fetch-repos.")
        open(OUT, "w").close()
        raise SystemExit(0)
    recs = []
    for lang, path in scan_queries(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        meta = parse_metadata(text)
        rid = meta.get("id") or path.stem
        name = meta.get("name") or rid
        desc = meta.get("description","")
        kind = meta.get("kind","problem")
        tags = (meta.get("tags") or []) + ["codeql"]
        recs.append(canon_record(
            source="codeql",
            language=lang,
            rule_id=rid,
            name=name,
            summary=desc[:180],
            description_md=desc,
            category="vulnerability" if "security" in [t.lower() for t in tags] or kind=="problem" else "code_smell",
            severity="major",
            tags=tags,
            mappings={},
            links={},
            meta={"ingest_source":"ql","file":str(path)}
        ))
    with open(OUT,"w",encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"codeql.jsonl written: {len(recs)} rules.")
