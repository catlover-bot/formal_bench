# -*- coding: utf-8 -*-
import json, sys

def ring_eq_cases(n=200):
    xs=[]
    for i in range(n):
        prop = "∀ x y : ℤ, (x + y)^2 = x^2 + 2*x*y + y^2"
        xs.append({"id": f"hard_ring_eq_{i}", "lean_prop": prop,
                   "split":"ood_topic","domain":"algebra","style":"eq"})
    return xs

def linarith_cases(n=200):
    xs=[]
    for i in range(n):
        prop = "∀ x y : ℚ, x ≤ y ∧ y ≤ x → x = y"
        xs.append({"id": f"hard_linarith_{i}", "lean_prop": prop,
                   "split":"ood_topic","domain":"order","style":"lin"})
    return xs

def nlinarith_cases(n=200):
    xs=[]
    for i in range(n):
        prop = "∀ x : ℝ, 0 ≤ (x - 3)^2"
        xs.append({"id": f"hard_nlin_{i}", "lean_prop": prop,
                   "split":"ood_topic","domain":"ineq","style":"nlin"})
    return xs

def main(out):
    data = ring_eq_cases(200) + linarith_cases(200) + nlinarith_cases(200)
    with open(out, "w", encoding="utf-8") as f:
        for ex in data:
            f.write(json.dumps(ex, ensure_ascii=False)+"\n")
    print(f"wrote {len(data)} to {out}")

if __name__=="__main__":
    out = sys.argv[1] if len(sys.argv)>1 else "data/hard_mix_v2.jsonl"
    main(out)
