import json, re, sys

ALLOWED = {"linarith","nlinarith","ring_nf","ring"}
CANON   = {
  "lin":"linarith", "nlin":"nlinarith",
  "ringnf":"ring_nf", "ring_nf_tac":"ring_nf", "ring_nf__tac":"ring_nf",
}

HEAD_RE = re.compile(r'^(linarith|nlinarith|ring_nf|ring)\b', re.I)

def canon(s: str) -> str:
    t = (s or "").strip()
    # ノイズ除去
    t = (t.replace("\u200b","").replace("\ufeff","")
           .replace("–","-").replace("—","-").replace("−","-"))
    # 先頭語を優先
    m = HEAD_RE.match(t)
    if m:
        return m.group(1)
    # だめなら英数下線の語を拾って代表形へ
    m2 = re.match(r'([A-Za-z_][A-Za-z0-9_]*)', t)
    w = (m2.group(1).lower() if m2 else "")
    w = w.rstrip("_")
    w = w.replace("ringnf","ring_nf")
    w = CANON.get(w, w)
    return w

def main(inp, outp):
    obj = json.load(open(inp, encoding="utf-8"))
    out = {}
    for k,v in obj.items():
        if isinstance(v, list) and v:
            head = canon(v[0])
        else:
            head = canon(str(v))
        # evaluator と同じ形式（id -> [line]）で出力
        out[k] = [head]
    json.dump(out, open(outp, "w", encoding="utf-8"), ensure_ascii=False)
    print("wrote", outp)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
