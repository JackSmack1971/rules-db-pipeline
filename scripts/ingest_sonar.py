\
#!/usr/bin/env python3
import os, json, time
import requests
from utils.common import ensure_dirs, NORM_DIR, canon_record

SONAR_BASE = os.environ.get("SONAR_BASE", "https://sonarcloud.io")
PAGE_SIZE = 500
OUT = NORM_DIR / "sonar.jsonl"

def fetch_rules(lang):
    p = 1
    total = None
    while True:
        url = f"{SONAR_BASE}/api/rules/search?languages={lang}&p={p}&ps={PAGE_SIZE}"
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        data = r.json()
        if total is None:
            total = data.get("total", 0)
        for rule in data.get("rules", []):
            yield rule
        if p * PAGE_SIZE >= total:
            break
        p += 1
        time.sleep(0.15)

def to_canonical(rule):
    desc = rule.get("htmlDesc") or rule.get("mdDesc") or ""
    mappings = {}
    if "cwe" in rule:
        mappings["cwe"] = rule.get("cwe", [])
    return canon_record(
        source="sonar",
        language=rule.get("lang") or "*",
        rule_id=rule.get("key") or "",
        name=rule.get("name",""),
        summary=rule.get("name",""),
        description_md=desc,
        category=(rule.get("type") or "CODE_SMELL").lower(),
        severity=(rule.get("severity") or "INFO"),
        tags=rule.get("tags",[]),
        mappings=mappings,
        links={"doc": rule.get("htmlUrl")},
        meta={"repo": rule.get("repo"), "ingest_source":"api"}
    )

if __name__ == "__main__":
    ensure_dirs()
    langs = os.environ.get("SONAR_LANGS","java,js,ts,py,cpp,cs,go,php,rb,kt").split(",")
    out = open(OUT, "w", encoding="utf-8")
    n=0
    for lang in langs:
        lang = lang.strip()
        try:
            for r in fetch_rules(lang):
                out.write(json.dumps(to_canonical(r), ensure_ascii=False) + "\n")
                n+=1
        except Exception as e:
            print(f"WARN: Sonar fetch failed for {lang}: {e}")
    out.close()
    print(f"sonar.jsonl written with {n} records (where available).")
