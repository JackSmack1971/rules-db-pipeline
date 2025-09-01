\
#!/usr/bin/env python3
import os, json, pathlib
from utils.common import ensure_dirs, NORM_DIR

OUT = NORM_DIR / "rules.jsonl"

if __name__ == "__main__":
    ensure_dirs()
    seen = set()
    count = 0
    with open(OUT, "w", encoding="utf-8") as sink:
        for path in sorted(NORM_DIR.glob("*.jsonl")):
            if path.name == "rules.jsonl": 
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        uid = obj.get("uid")
                        if uid in seen: 
                            continue
                        seen.add(uid)
                        sink.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        count += 1
            except FileNotFoundError:
                continue
    print(f"Consolidated {count} unique rules to {OUT}.")
