import json, random, sys
random.seed(0)

def ring_cases(n=100):
    xs=[]
    for _ in range(n):
        # 多項式等式（simp では閉じにくい、ring なら一発）
        a,b,c = [random.randint(-5,5) for _ in range(3)]
        prop = f"∀ x y z : ℤ, ((x + {a})*(y + {b}) + z*{c})^2 = ((x + {a})*(y + {b}) + z*{c})*((x + {a})*(y + {b}) + z*{c})"
        xs.append({"id": f"hard_ring_{_}", "lean_prop": prop, "split":"ood_style","domain":"algebra","style":"contest"})
    return xs

def nlinarith_cases(n=100):
    xs=[]
    for _ in range(n):
        # 非線形不等式（ℝ の平方非負）：nlinarith で閉じる
        prop = "∀ x : ℝ, x^2 ≥ 0"
        xs.append({"id": f"hard_nlinarith_{_}", "lean_prop": prop, "split":"ood_topic","domain":"algebra","style":"textbook"})
    return xs

def main(out):
    data = ring_cases(80)+nlinarith_cases(20)
    with open(out,"w",encoding="utf-8") as f:
        for ex in data:
            f.write(json.dumps(ex, ensure_ascii=False)+"\n")
    print(f"wrote {len(data)} to {out}")

if __name__=="__main__":
    out = sys.argv[1] if len(sys.argv)>1 else "data/hard_mix.jsonl"
    main(out)
