#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random, json
from pathlib import Path

# 生成する命題は「必ず真」に寄せます（参加者が証明可能）。
# たとえば False を含めると“必ず失敗”なので、評価には混ぜず control 用に分けるのが無難。
# ここでは真の命題のみを出します。

DOMAINS = ["algebra", "number_theory", "combinatorics"]
STYLES  = ["textbook", "contest"]

def mk_algebra():
    a = random.randint(0, 20); b = random.randint(0, 20)
    props = [
        f"{a} + {b} = {a+b}",
        f"{a} * {b} = {a*b}",
        f"{a} ≤ {a+b}",
        f"¬ ({a+b} < {a})",
    ]
    return random.choice(props)

def mk_number_theory():
    from math import gcd
    a = random.randint(1, 30); b = random.randint(1, 30)
    g = gcd(a,b)
    props = [
        f"Nat.gcd {a} {b} = {g}",
        f"{a} ∣ {a*b}",  # a divides a*b
        f"{b} ∣ {a*b}",
        f"¬ ({a} ∣ {b})" if (b % a != 0) else f"{a} ∣ {b}",
    ]
    return random.choice(props)

def fact(n):
    r=1
    for i in range(1,n+1): r*=i
    return r

def nCk(n,k):
    if k<0 or k>n: return 0
    return fact(n)//(fact(k)*fact(n-k))

def mk_combinatorics():
    n = random.randint(1, 8)
    k = random.randint(0, n)
    val = nCk(n,k)
    # mathlib の choose 記法：Nat.choose n k
    props = [
        f"Nat.choose {n} {k} = {val}",
        f"{val} ≤ {2**n}",
        f"{val} ≤ {fact(n)}",
        f"¬ (Nat.choose {n} {k} = 0)" if 0<k<n else f"Nat.choose {n} {k} = 1"
    ]
    return random.choice(props)

GEN = {
    "algebra": mk_algebra,
    "number_theory": mk_number_theory,
    "combinatorics": mk_combinatorics,
}

def unique_id(domain, style, idx):
    prefix = {"algebra":"ALG","number_theory":"NT","combinatorics":"COM"}[domain]
    st = {"textbook":"TB","contest":"CO"}[style]
    return f"{prefix}-{st}-{idx:05d}"

def gen_items(n_id=150, n_ood_style=25, n_ood_topic=25, seed=0):
    random.seed(seed)
    items = []

    # ID: domain固定（例：algebra, number_theory の2ドメイン）+ style=textbook
    id_domains = ["algebra", "number_theory"]
    style = "textbook"
    idx = 1
    for _ in range(n_id):
        dom = random.choice(id_domains)
        prop = GEN[dom]()
        items.append({
            "id": unique_id(dom, style, idx),
            "split": "id",
            "domain": dom,
            "style": style,
            "difficulty": random.randint(1,3),
            "lean_prop": prop
        })
        idx += 1

    # OOD-Style: 同じドメインで style を contest に
    style = "contest"
    for _ in range(n_ood_style):
        dom = random.choice(id_domains)
        prop = GEN[dom]()
        items.append({
            "id": unique_id(dom, style, idx),
            "split": "ood_style",
            "domain": dom,
            "style": style,
            "difficulty": random.randint(1,3),
            "lean_prop": prop
        })
        idx += 1

    # OOD-Topic: 未見ドメイン（例：combinatorics）をテストに投入
    style = "textbook"
    dom = "combinatorics"
    for _ in range(n_ood_topic):
        prop = GEN[dom]()
        items.append({
            "id": unique_id(dom, style, idx),
            "split": "ood_topic",
            "domain": dom,
            "style": style,
            "difficulty": random.randint(1,3),
            "lean_prop": prop
        })
        idx += 1

    return items

def main():
    import argparse, orjson, hashlib
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/test.jsonl")
    ap.add_argument("--id", type=int, default=20)          # 最初は小さく
    ap.add_argument("--ood_style", type=int, default=5)
    ap.add_argument("--ood_topic", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    items = gen_items(args.id, args.ood_style, args.ood_topic, args.seed)

    # 重複除去（命題文字列の正規化ハッシュ）
    seen = set(); out = []
    for it in items:
        key = it["lean_prop"].replace(" ", "")
        h = hashlib.sha1(key.encode()).hexdigest()
        if h in seen: continue
        seen.add(h); out.append(it)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for it in out:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    print(f"wrote {len(out)} examples to {args.out}")

if __name__ == "__main__":
    main()
