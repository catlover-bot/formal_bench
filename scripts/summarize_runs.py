import argparse, json, re, time, glob, pathlib, collections, csv
PAT = re.compile(r'^(linarith|nlinarith|ring_nf|ring|simp|norm_num|taut|aesop)\b', re.ASCII)
def norm_head(w):
    w=(w or "").split()[0]; m=PAT.match(w)
    if m: return m.group(1)
    w=re.sub(r'\[.*\]$','',w).replace('ringuff','ring').replace('ring_eq','ring')
    for b in ("linarith","nlinarith","ring_nf","ring"):
        if w.startswith(b): return b
    return w
def load_styles(bench):
    styles={}
    for l in open(bench):
        ex=json.loads(l); styles[ex["id"]]=ex.get("style","")
    return styles
def score(path, styles):
    d=json.load(open(path)); ok=tot=0
    for k,v in d.items():
        if not v or not v[0]: continue
        h=norm_head(v[0]); st=styles.get(k,""); tot+=1
        if st=="eq" and h in {"ring_nf","ring"}: ok+=1
        elif st=="lin" and h=="linarith": ok+=1
        elif st=="nlin" and h=="nlinarith": ok+=1
    return ok, tot
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--bench", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("files", nargs="+")
    a=ap.parse_args()
    styles=load_styles(a.bench)
    rows=[]
    for pat in a.files:
        for p in sorted(glob.glob(pat)):
            pth=pathlib.Path(p); name=pth.stem
            # 推定: ファイル名から model / T をゆるく抽出
            model = "gpt4o-mini" if "gpt4o" in name else ("claude-3.5-sonnet" if "claude" in name else "other")
            m = re.search(r'_t(\d+)$', name)
            T = int(m.group(1)) if m else None
            ok,tot = score(p, styles)
            rows.append({"file":pth.name,"model":model,"max_tokens":T,"ok":ok,"tot":tot,"acc":ok/tot if tot else 0.0})
    with open(a.out,"w",newline="") as f:
        w=csv.DictWriter(f, fieldnames=["file","model","max_tokens","ok","tot","acc"])
        w.writeheader(); w.writerows(rows)
    print("wrote", a.out, len(rows), "rows")
if __name__=="__main__":
    main()
