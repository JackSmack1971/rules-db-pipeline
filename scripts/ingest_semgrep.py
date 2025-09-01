\
#!/usr/bin/env python3
import os, json, yaml, pathlib
from utils.common import ensure_dirs, VENDOR_DIR, NORM_DIR, canon_record

OUT = NORM_DIR / "semgrep.jsonl"

def walk_yaml(root):
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith((".yml",".yaml")):
                yield os.path.join(dirpath, f)

def ingest():
    root = VENDOR_DIR / "semgrep-rules"
    if not root.exists():
        print("WARN: semgrep-rules repo not present; run fetch-repos or skip.")
        return []
    recs = []
    for path in walk_yaml(str(root)):
        try:
            y = yaml.safe_load(open(path,"r",encoding="utf-8"))
        except Exception as e:
            print("WARN: YAML parse failed", path, e)
            continue
        rules = y.get("rules") or []
        for r in rules:
            rid = r.get("id") or r.get("rule","")
            langs = r.get("languages") or ["*"]
            desc = r.get("message","")
            sev  = r.get("severity") or "info"
            meta = r.get("metadata") or {}
            recs.append(canon_record(
                source="semgrep",
                language=langs,
                rule_id=rid,
                name=meta.get("shortdesc") or rid,
                summary=desc[:180],
                description_md=desc,
                category="vulnerability" if "cwe" in meta else "code_smell",
                severity=sev,
                tags=(meta.get("tags") or []) + ["semgrep"],
                mappings={"cwe": meta.get("cwe", []), "owasp_asvs": meta.get("owasp", [])},
                links={"doc": (meta.get("references") or [None])[0]},
                meta={"ingest_source":"yaml","file":path}
            ))
    return recs

if __name__ == "__main__":
    ensure_dirs()
    recs = ingest()
    with open(OUT, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"semgrep.jsonl written: {len(recs)} records.")
