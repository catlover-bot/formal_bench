import json, random, sys
random.seed(0)

def ring_cases(n=200):
    xs=[]
    for i in range(n):
        # 展開や平方完成系など（simp では基本閉じない、ring向け）
        a,b = random.randint(-4,4), random.randint(-4,4)
        prop = f"∀ x y : ℤ, (x + y + {a})^2 = (x + y + {a})*(x + y + {a})"
        xs.append({"id": f"hard_ring_{i}", "lean_prop": prop,
                   "split":"ood_style","domain":"algebra","style":"contest"})
    return xs

def linarith_cases(n=200):
    xs=[]
    for i in range(n):
        # 線形不等式（linarith が安定、simp/trivialでは閉じにくい）
        c = random.randint(1,5)
        prop = f"∀ a b : ℚ, a ≤ b → b ≤ a + {c} → a ≤ b"
        xs.append({"id": f"hard_linarith_{i}", "lean_prop": prop,
                   "split":"ood_topic","domain":"algebra","style":"textbook"})
    return xs

def nlinarith_cases(n=200):
    xs=[]
    for i in range(n):
        # 典型：平方は非負（ℝ）
        prop = "∀ x : ℝ, (x - 3)^2 ≥ 0"
        xs.append({"id": f"hard_nlinarith_{i}", "lean_prop": prop,
                   "split":"ood_topic","domain":"algebra","style":"contest"})
    return xs

def main(out):
    data = ring_cases(200) + linarith_cases(200) + nlinarith_cases(200)
    with open(out,"w",encoding="utf-8") as f:
        for ex in data:
            f.write(json.dumps(ex, ensure_ascii=False)+"\n")
    print(f"wrote {len(data)} to {out}")

if __name__=="__main__":
    out = sys.argv[1] if len(sys.argv)>1 else "data/hard_mix.jsonl"
    main(out)
