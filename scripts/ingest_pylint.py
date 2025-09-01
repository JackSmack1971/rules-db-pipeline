\
#!/usr/bin/env python3
import re, json
from utils.common import ensure_dirs, NORM_DIR, have_exe, run, canon_record

OUT = NORM_DIR / "pylint.jsonl"

def ingest():
    if not have_exe("pylint"):
        print("WARN: pylint not found; skipping.")
        return []
    # Use --list-msgs to get a compact list; format varies by version.
    res = run(["pylint", "--list-msgs"])
    if res.returncode != 0:
        print("WARN: pylint --list-msgs failed; stderr:", res.stderr.strip())
        return []
    recs = []
    # Sample line formats vary; handle id, symbol, category code at start.
    for line in res.stdout.splitlines():
        m = re.match(r"^\s*([CRWEF]):\s*\(([^)]+)\)\s*([\w-]+)\s*:\s*(.+)", line.strip())
        if not m: 
            # Try alternative: "msg-id (symbol): description"
            m2 = re.match(r"^\s*([\w-]+)\s*\(([^)]+)\)\s*:\s*(.+)", line.strip())
            if not m2:
                continue
            cat = "W"; symbol = m2.group(2); msgid = m2.group(1); desc = m2.group(3)
        else:
            cat, symbol, msgid, desc = m.groups()
        recs.append(canon_record(
            source="pylint",
            language="py",
            rule_id=msgid,
            name=symbol or msgid,
            summary=desc[:180],
            description_md=desc,
            category={"C":"style","R":"refactor","W":"warning","E":"error","F":"fatal"}.get(cat,"code_smell"),
            severity=cat.lower(),
            tags=["pylint"],
            mappings={},
            links={},
            meta={"ingest_source":"cli"}
        ))
    return recs

if __name__ == "__main__":
    ensure_dirs()
    recs = ingest()
    with open(OUT,"w",encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"pylint.jsonl written: {len(recs)} rules.")
