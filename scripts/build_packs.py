\
#!/usr/bin/env python3
import os, json, pathlib, collections
from utils.common import ensure_dirs, NORM_DIR

SRC = NORM_DIR / "rules.jsonl"
PP_DIR = (SRC.parent.parent) / "policy-packs"

WEIGHTS = {
  "consistency": {"style":0.7,"convention":0.7},
  "intentionality": {"dead_code":0.6,"complexity":0.6,"unused":0.6},
  "adaptability": {"design":0.6,"code_smell":0.6,"architecture":0.7,"refactor":0.6},
  "responsibility": {"vulnerability":0.8,"security":0.8,"privacy":0.7,"injection":0.8}
}

SEV_WEIGHT = {"info":0.0,"minor":0.1,"major":0.3,"critical":0.6,"blocker":0.8}

def infer_quality(rec):
    tags = set((rec.get("tags") or []) + [rec.get("category","")])
    q = {k:0.0 for k in WEIGHTS}
    for axis, m in WEIGHTS.items():
        for t,w in m.items():
            if t in tags: q[axis] = max(q[axis], w)
    sev = SEV_WEIGHT.get(rec.get("severity","info"), 0.0)
    for k in q: q[k] = min(1.0, q[k] + sev*0.4)
    rec["quality"] = {**q, "rationale":"heuristic"}
    return rec

if __name__ == "__main__":
    ensure_dirs()
    PP_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    with open(SRC, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): 
                continue
            rec = json.loads(line)
            records.append(infer_quality(rec))

    buckets = collections.defaultdict(list)
    for r in records:
        langs = r.get("language") or ["*"]
        for lang in langs:
            for axis in ["adaptability","consistency","intentionality","responsibility"]:
                if r["quality"][axis] >= 0.6:
                    buckets[(lang, axis)].append(r)

    # write packs
    for (lang, axis), items in buckets.items():
        path = PP_DIR / lang / f"{axis}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for it in sorted(items, key=lambda x: (-x["quality"][axis], x["severity"], x["name"])):
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print("Policy packs written under rules-db/policy-packs/")
