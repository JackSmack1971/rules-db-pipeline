\
#!/usr/bin/env python3
import json
from utils.common import ensure_dirs, NORM_DIR, have_exe, run, canon_record

OUT = NORM_DIR / "clang_tidy.jsonl"

if __name__ == "__main__":
    ensure_dirs()
    if not have_exe("clang-tidy"):
        print("WARN: clang-tidy not found; skipping.")
        open(OUT, "w").close()
        raise SystemExit(0)
    res = run(["clang-tidy", "--list-checks", "-checks=*"])
    if res.returncode != 0:
        print("WARN: clang-tidy --list-checks failed:", res.stderr.strip())
        open(OUT, "w").close()
        raise SystemExit(0)
    recs = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("Enabled checks"):
            continue
        rid = line.split()[0]
        recs.append(canon_record(
            source="clang-tidy",
            language=["cpp","c"],
            rule_id=rid,
            name=rid,
            summary=rid,
            description_md="",
            category="code_smell",
            severity="major",
            tags=["clang-tidy"],
            mappings={},
            links={"doc": f"https://clang.llvm.org/extra/clang-tidy/checks/{rid}.html"},
            meta={"ingest_source":"cli"}
        ))
    with open(OUT,"w",encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"clang_tidy.jsonl written: {len(recs)} rules.")
