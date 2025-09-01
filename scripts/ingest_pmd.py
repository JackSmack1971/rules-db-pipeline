\
#!/usr/bin/env python3
import os, json, pathlib, xml.etree.ElementTree as ET
from utils.common import ensure_dirs, VENDOR_DIR, NORM_DIR, canon_record, norm_sev

OUT = NORM_DIR / "pmd.jsonl"

def find_xml_rules():
    root = VENDOR_DIR / "pmd"
    if not root.exists():
        return []
    # PMD rules are under category/<lang>/*.xml (modern layout)
    paths = list(root.glob("**/category/**/**/*.xml"))
    if not paths:
        # Fallback older layout
        paths = list(root.glob("**/rulesets/**/*.xml"))
    return paths

def pmd_priority_to_sev(p):
    # PMD priority 1..5 (1 is highest)
    return {"1":"blocker","2":"critical","3":"major","4":"minor","5":"info"}.get(str(p),"info")

if __name__ == "__main__":
    ensure_dirs()
    recs = []
    for xml_path in find_xml_rules():
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception as e:
            # Skip non-rule XMLs
            continue
        lang = xml_path.as_posix().split("/category/")[-1].split("/")[0] if "/category/" in xml_path.as_posix() else "*"
        for rule in root.findall(".//rule"):
            rid = rule.get("name") or rule.get("ref") or ""
            msg = rule.get("message") or ""
            desc_el = rule.find("description")
            desc = (desc_el.text or "").strip() if desc_el is not None else msg
            pri = rule.get("priority") or "3"
            recs.append(canon_record(
                source="pmd",
                language=lang,
                rule_id=rid,
                name=rid,
                summary=msg or desc[:180],
                description_md=desc,
                category="code_smell",
                severity=pmd_priority_to_sev(pri),
                tags=["pmd"],
                mappings={},
                links={},
                meta={"ingest_source":"xml","file":str(xml_path)}
            ))
    with open(OUT,"w",encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"pmd.jsonl written: {len(recs)} rules.")
