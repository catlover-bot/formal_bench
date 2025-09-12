#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random, json, hashlib, math
from pathlib import Path

DOMAINS = ["algebra", "number_theory", "combinatorics"]
STYLES  = ["textbook", "contest"]

def mk_algebra(r):
    a, b = r.randint(0, 40), r.randint(0, 40)
    c = r.randint(0, 40)
    return r.choice([
        f"{a} + {b} = {a+b}",
        f"{a} * {b} = {a*b}",
        f"{a} ≤ {a+b}",
        f"¬ ({a+b} < {a})",
        f"{a} + {b} + {c} = {a+b+c}",
        f"{a} * ({b} + {c}) = {a*(b+c)}",
    ])

def mk_number_theory(r):
    from math import gcd
    a, b = r.randint(1, 60), r.randint(1, 60)
    g = gcd(a,b)
    # 分かりやすい整除・非整除を混ぜる
    div_true = r.choice([f"{a} ∣ {a*b}", f"{b} ∣ {a*b}"])
    div_false = f"¬ ({a} ∣ {b})" if (b % a != 0) else f"{a} ∣ {b}"
    return r.choice([
        f"Nat.gcd {a} {b} = {g}",
        div_true,
        div_false,
    ])

def fact(n):
    x=1
    for i in range(1,n+1): x*=i
    return x

def nCk(n,k):
    if k<0 or k>n: return 0
    return fact(n)//(fact(k)*fact(n-k))

def mk_combinatorics(r):
    n = r.randint(1, 9)
    k = r.randint(0, n)
    val = nCk(n,k)
    return r.choice([
        f"Nat.choose {n} {k} = {val}",
        f"{val} ≤ {2**n}",
        f"{val} ≤ {fact(n)}",
        f"¬ (Nat.choose {n} {k} = 0)" if 0<k<n else f"Nat.choose {n} {k} = 1"
    ])

GEN = {
    "algebra": mk_algebra,
    "number_theory": mk_number_theory,
    "combinatorics": mk_combinatorics,
}

def uid(dom, sty, idx):
    mp = {"algebra":"ALG","number_theory":"NT","combinatorics":"COM"}[dom]
    st = {"textbook":"TB","contest":"CO"}[sty]
    return f"{mp}-{st}-{idx:05d}"

def shingles(s, k=3):
    s = s.replace(" ", "")
    return { s[i:i+k] for i in range(max(0, len(s)-k+1)) } or {s}

def near_dup_filter(items, jaccard_lo=0.9):
    kept = []
    sigs = []
    for it in items:
        S = shingles(it["lean_prop"])
        keep = True
        for T in sigs:
            inter = len(S & T); uni = len(S | T)
            if uni and inter/uni >= jaccard_lo:
                keep = False; break
        if keep:
            kept.append(it); sigs.append(S)
    return kept

def gen(seed, n_id, n_ood_style, n_ood_topic):
    r = random.Random(seed)
    out = []
    # ID: 2ドメイン固定 + textbook
    id_domains = ["algebra", "number_theory"]
    idx = 1
    for _ in range(n_id):
        d = r.choice(id_domains)
        p = GEN[d](r)
        out.append({
            "id": uid(d, "textbook", idx),
            "split": "id",
            "domain": d,
            "style": "textbook",
            "difficulty": r.randint(1,3),
            "lean_prop": p,
            "license": "CC0",
            "source": {"kind":"synthetic","seed":seed}
        }); idx+=1
    # OOD-Style
    for _ in range(n_ood_style):
        d = r.choice(id_domains)
        p = GEN[d](r)
        out.append({
            "id": uid(d, "contest", idx),
            "split": "ood_style",
            "domain": d,
            "style": "contest",
            "difficulty": r.randint(1,3),
            "lean_prop": p,
            "license": "CC0",
            "source": {"kind":"synthetic","seed":seed}
        }); idx+=1
    # OOD-Topic: 新ドメイン combinatorics
    for _ in range(n_ood_topic):
        p = GEN["combinatorics"](r)
        out.append({
            "id": uid("combinatorics", "textbook", idx),
            "split": "ood_topic",
            "domain": "combinatorics",
            "style": "textbook",
            "difficulty": r.randint(1,3),
            "lean_prop": p,
            "license": "CC0",
            "source": {"kind":"synthetic","seed":seed}
        }); idx+=1

    # 厳しめ重複・近縁重複除去
    out = near_dup_filter(out, jaccard_lo=0.90)
    return out

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/test.jsonl")
    ap.add_argument("--id", type=int, default=800)
    ap.add_argument("--ood_style", type=int, default=100)
    ap.add_argument("--ood_topic", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    items = gen(args.seed, args.id, args.ood_style, args.ood_topic)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out,"w",encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"wrote {len(items)} to {args.out} (seed={args.seed})")

if __name__ == "__main__":
    main()
