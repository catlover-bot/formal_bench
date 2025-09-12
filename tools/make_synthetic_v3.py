#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random, json
from pathlib import Path

R = random.Random

# ---- 既存の「易しめ」パターン（v2相当の一部） ----
def easy_algebra(r:R):
    a,b,c = r.randint(0,40), r.randint(0,40), r.randint(0,40)
    return r.choice([
        f"{a} + {b} = {a+b}",
        f"{a} * {b} = {a*b}",
        f"{a} ≤ {a+b}",
        f"¬ ({a+b} < {a})",
        f"{a} * ({b} + {c}) = {a*(b+c)}",
    ])

def easy_number_theory(r:R):
    from math import gcd
    a,b = r.randint(1,60), r.randint(1,60)
    g = gcd(a,b)
    div_true  = r.choice([f"{a} ∣ {a*b}", f"{b} ∣ {a*b}"])
    div_maybe = f"¬ ({a} ∣ {b})" if (b % a != 0) else f"{a} ∣ {b}"
    return r.choice([f"Nat.gcd {a} {b} = {g}", div_true, div_maybe])

def fact(n): 
    x=1
    for i in range(1,n+1): x*=i
    return x

def nCk(n,k):
    if k<0 or k>n: return 0
    from math import factorial
    return factorial(n)//(factorial(k)*factorial(n-k))

def easy_combinatorics(r:R):
    n = r.randint(1,9); k = r.randint(0,n)
    val = nCk(n,k)
    return r.choice([
        f"Nat.choose {n} {k} = {val}",
        f"{val} ≤ {2**n}",
        f"{val} ≤ {fact(n)}",
        f"¬ (Nat.choose {n} {k} = 0)" if 0<k<n else f"Nat.choose {n} {k} = 1"
    ])

# ---- “Hard” パターン（量化子・存在・論理構造） ----
# simp/trivial/exact では通らず、aesop 等が必要になりやすい
def hard_algebra(r:R):
    return r.choice([
        # 反射率・推移を使う系
        "∀ a b c : Nat, a ≤ b → a ≤ b + c",
        "∀ a b : Nat, a ≤ b ∧ b ≤ a → a = b",
        # 存在公理（加法による分解）
        "∀ a b : Nat, a ≤ b → ∃ c, b = a + c",
        # 全順序の一部（選言）
        "∀ a b : Nat, a ≤ b ∨ b ≤ a",
    ])

def hard_number_theory(r:R):
    return r.choice([
        # 整除の加法閉性（dvd_add）
        "∀ a b c : Nat, a ∣ b → a ∣ c → a ∣ b + c",
        # 連鎖（∧ 形）
        "∀ a b c : Nat, a ∣ b ∧ a ∣ c → a ∣ b + c",
        # 互いに素と乗法を絡める（coprime → 左因子がかかっても片側に落とす）
        "∀ a b c : Nat, Nat.gcd a b = 1 ∧ a ∣ b * c → a ∣ c",
        # 倍数の反射（存在の導入）
        "∀ a b : Nat, a ∣ b → ∃ k, b = a * k",
    ])

def hard_combinatorics(r:R):
    n = r.randint(1,9)
    return r.choice([
        # choose の端点（定番・証明は必要）
        f"∀ n : Nat, Nat.choose n 0 = 1",
        f"∀ n : Nat, Nat.choose n n = 1",
        # 上界（安全側：2^n 上限）
        f"∀ n k : Nat, k ≤ n → Nat.choose n k ≤ (Nat.pow 2 n)",
    ])

EASY = {
    ("algebra","textbook"): easy_algebra,
    ("number_theory","textbook"): easy_number_theory,
    ("combinatorics","textbook"): easy_combinatorics,
}
HARD = {
    ("algebra","textbook"): hard_algebra,
    ("number_theory","textbook"): hard_number_theory,
    ("combinatorics","textbook"): hard_combinatorics,
}

def uid(dom, sty, idx):
    mp = {"algebra":"ALG","number_theory":"NT","combinatorics":"COM"}[dom]
    st = {"textbook":"TB","contest":"CO"}[sty]
    return f"{mp}-{st}-{idx:06d}"

def gen(seed:int, n_id:int, n_ood_style:int, n_ood_topic:int, hard_frac:float):
    r = R(seed)
    out=[]; idx=1
    id_domains=["algebra","number_theory"]  # OOD-topic 用に combinatorics は除外

    def push(split, dom, sty, prop, diff):
        nonlocal idx
        out.append({
            "id": uid(dom, sty, idx),
            "split": split, "domain": dom, "style": sty,
            "difficulty": diff, "lean_prop": prop,
            "license": "CC0", "source": {"kind":"synthetic", "seed": seed}
        }); idx += 1

    # ID: textbook, hard/easy を混ぜる
    for _ in range(n_id):
        dom = r.choice(id_domains)
        if r.random() < hard_frac:
            push("id", dom, "textbook", HARD[(dom,"textbook")](r), diff=3)
        else:
            push("id", dom, "textbook", EASY[(dom,"textbook")](r), diff=r.randint(1,2))

    # OOD-Style: 同ドメインで contest 表現（命題は textbook と同質）
    for _ in range(n_ood_style):
        dom = r.choice(id_domains)
        if r.random() < hard_frac:
            push("ood_style", dom, "contest", HARD[(dom,"textbook")](r), diff=3)
        else:
            push("ood_style", dom, "contest", EASY[(dom,"textbook")](r), diff=r.randint(1,2))

    # OOD-Topic: combinatorics
    for _ in range(n_ood_topic):
        if r.random() < hard_frac:
            push("ood_topic", "combinatorics", "textbook", HARD[("combinatorics","textbook")](r), diff=3)
        else:
            push("ood_topic", "combinatorics", "textbook", EASY[("combinatorics","textbook")](r), diff=r.randint(1,2))

    return out

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default="data/test_v3.jsonl")
    ap.add_argument("--id", type=int, default=2000)
    ap.add_argument("--ood_style", type=int, default=600)
    ap.add_argument("--ood_topic", type=int, default=600)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--hard_frac", type=float, default=0.6)  # Hard を何割入れるか
    args=ap.parse_args()

    items = gen(args.seed, args.id, args.ood_style, args.ood_topic, args.hard_frac)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out,"w",encoding="utf-8") as f:
        for it in items: f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"wrote {len(items)} to {args.out} (seed={args.seed}, hard={args.hard_frac})")

if __name__=="__main__":
    main()
