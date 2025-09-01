\
#!/usr/bin/env python3
import os, json, pathlib, xml.etree.ElementTree as ET
from utils.common import ensure_dirs, VENDOR_DIR, NORM_DIR, canon_record

OUT = NORM_DIR / "checkstyle.jsonl"

def find_checks():
    root = VENDOR_DIR / "checkstyle"
    if not root.exists():
        return []
    # Common configs
    return [root / "src" / "main" / "resources" / "google_checks.xml",
            root / "src" / "main" / "resources" / "sun_checks.xml"]

if __name__ == "__main__":
    ensure_dirs()
    recs = []
    for cfg in find_checks():
        if not cfg.exists(): 
            continue
        try:
            tree = ET.parse(cfg)
            root = tree.getroot()
        except Exception as e:
            continue
        for mod in root.findall(".//module"):
            name = mod.get("name") or "Module"
            # Treat each module as a 'rule'
            props = []
            for p in mod.findall("property"):
                props.append(f"{p.get('name')}={p.get('value')}")
            desc = f"Checkstyle module `{name}` with properties: " + ", ".join(props)
            recs.append(canon_record(
                source="checkstyle",
                language="java",
                rule_id=name,
                name=name,
                summary=f"Checkstyle {name}",
                description_md=desc,
                category="style",
                severity="major",
                tags=["checkstyle"],
                mappings={},
                links={"doc":"https://checkstyle.org/checks.html"},
                meta={"ingest_source":"xml","file":str(cfg)}
            ))
    with open(OUT,"w",encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"checkstyle.jsonl written: {len(recs)} rules.")
