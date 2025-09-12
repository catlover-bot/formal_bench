#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, collections, random
from pathlib import Path

TARGET = {
  ("id","algebra","textbook"): 400,
  ("id","number_theory","textbook"): 400,
  ("ood_style","algebra","contest"): 100,
  ("ood_style","number_theory","contest"): 100,
  ("ood_topic","combinatorics","textbook"): 100,
}

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", default="data/validated.jsonl")
    ap.add_argument("--out", default="data/bench_v0_1.jsonl")
    ap.add_argument("--seed", type=int, default=0)
    args=ap.parse_args()
    random.seed(args.seed)

    buckets=collections.defaultdict(list)
    for ln in open(args.input,"r",encoding="utf-8"):
        ex=json.loads(ln)
        key=(ex["split"], ex["domain"], ex["style"])
        if not ex.get("cc_ok"): continue
        buckets[key].append(ex)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    n_total=0
    with open(args.out,"w",encoding="utf-8") as f:
        for key, need in TARGET.items():
            pool = buckets.get(key, [])
            if len(pool)<need:
                print(f"[WARN] {key} only {len(pool)} available; taking all.")
                take = pool
            else:
                # 難易度バランス（1/2/3 を均等目標）
                byd = {1:[],2:[],3:[]}
                for ex in pool:
                    byd[ex.get("difficulty",2)].append(ex)
                # まず難易度バランス（1/2/3）
                target_each = max(1, need//3)
                take=[]
                for d in (1,2,3):
                    random.shuffle(byd[d])
                    take += byd[d][:min(len(byd[d]), target_each)]

                # Hard(=3) を最低30%まで確保
                hard_min = max(1, int(need * 0.30))
                cur_hard = sum(1 for e in take if e.get("difficulty",2)==3)
                if cur_hard < hard_min:
                    more = [e for e in byd[3] if e not in take]
                    random.shuffle(more)
                    take += more[:max(0, hard_min - cur_hard)]

                # まだ不足分を残りから補充
                remain = [e for e in pool if e not in take]
                random.shuffle(remain)
                while len(take)<need and remain:
                    take.append(remain.pop())
            for ex in take:
                # 公開用：内部チェック情報を落とす
                ex.pop("cc_ok",None); ex.pop("cc_tactic",None); ex.pop("cc_time",None)
                f.write(json.dumps(ex,ensure_ascii=False)+"\n")
            n_total += len(take)

    # プロベナンス
    prov = {
      "license":"CC0-1.0",
      "seed": args.seed,
      "counts": {f"{k}": TARGET[k] for k in TARGET},
      "generated_by": "tools/make_synthetic_v2.py + tools/cc_validate.py + tools/pack_benchmark.py",
    }
    Path("data/provenance.json").write_text(json.dumps(prov,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"packed": n_total, "out": args.out}, ensure_ascii=False))

if __name__=="__main__":
    main()
