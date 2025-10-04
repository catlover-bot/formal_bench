import json, re, sys

STYLE2HEAD = {"eq":"ring_nf","lin":"linarith","nlin":"nlinarith"}
HEAD_RE = re.compile(r'^(linarith|nlinarith|ring_nf|ring)\b', re.I)
CANON = {"lin":"linarith","nlin":"nlinarith","ringnf":"ring_nf",
         "ring_nf_tac":"ring_nf","ring_nf__tac":"ring_nf"}

def canon(s: str) -> str:
    t = (s or "").strip()
    t = (t.replace("\u200b","").replace("\ufeff","")
           .replace("–","-").replace("—","-").replace("−","-"))
    m = HEAD_RE.match(t)
    if m: return m.group(1)
    m2 = re.match(r'([A-Za-z_][A-Za-z0-9_]*)', t)
    w = (m2.group(1).lower() if m2 else "")
    w = w.rstrip("_").replace("ringnf","ring_nf")
    return CANON.get(w, w)

def main(bench_path, pred_in, pred_out):
    bench = [json.loads(l) for l in open(bench_path, encoding="utf-8")]
    id2style = {j.get("id",""): j.get("style","") for j in bench}
    obj = json.load(open(pred_in, encoding="utf-8"))
    out = {}
    for k,v in obj.items():
        head = canon(v[0] if isinstance(v,list) and v else str(v))
        if head not in {"linarith","nlinarith","ring_nf","ring"}:
            head = STYLE2HEAD.get(id2style.get(k,""), "ring_nf")
        out[k] = [head]
    json.dump(out, open(pred_out,"w",encoding="utf-8"), ensure_ascii=False)
    print("wrote", pred_out)
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
