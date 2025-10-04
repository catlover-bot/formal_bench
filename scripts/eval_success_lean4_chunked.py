import re
import argparse, json, os, subprocess, time, re
from pathlib import Path

HEAD_RE = re.compile(r'^(linarith|nlinarith|ring_nf|ring)\b')
CANON = {
  "linarith":"linarith","lin":"linarith",
  "nlinarith":"nlinarith","nlin":"nlinarith",
  "ring_nf":"ring_nf","ringnf":"ring_nf",
  "ring":"ring"
}

def _first_word_token(t: str) -> str:
    # 雑音の除去（ゼロ幅/BOM/ダッシュ類を正規化）
    t = (t or "").strip().replace("\u200b","").replace("\ufeff","")
    t = t.replace("–","-").replace("—","-").replace("−","-")
    m = re.match(r'([A-Za-z_][A-Za-z0-9_]*)', t)
    return m.group(1) if m else ""

HDR = """\
import Mathlib
set_option autoImplicit false
set_option maxRecDepth 10000
set_option maxHeartbeats 200000
"""

def sanitize(t: str) -> str:
    if not t: return ""
    t = t.strip()
    if t.endswith("."): t = t[:-1]
    m = HEAD_RE.match(t)
    return m.group(1) if m else t

def load_bench(p):
    xs=[]
    with open(p,encoding="utf-8") as f:
        for l in f:
            j=json.loads(l)
            xs.append((j.get("id",""),
                       j.get("lean_prop") or j.get("goal") or j.get("statement") or "",
                       j.get("style","")))
    return xs

def load_preds(p):
    obj=json.load(open(p,encoding="utf-8"))
    return {k:(v[0] if isinstance(v,list) and v else "") for k,v in obj.items()}

def write_chunk(root:Path, chunk_id:int, cases, prelude:str)->Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"Batch_{chunk_id:03d}.lean"
    lines=[HDR, ""]
    for i,(gid,goal,tac) in enumerate(cases):
        thm = f"""\
/-- {gid} -/
theorem _case_{chunk_id:03d}_{i:03d} : {goal} := by
  {prelude}
  {tac}
"""
        lines.append(thm)
    path.write_text("\n".join(lines),encoding="utf-8")
    return path

def run_lean(workdir:Path, f:Path, timeout:int):
    r = subprocess.run(["lake","env","lean",str(f)], cwd=str(workdir),
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    return r.returncode==0, r.stdout.decode("utf-8","ignore")

def main(a):
    bench = load_bench(a.bench)
    preds = load_preds(a.preds)
    prelude = os.environ.get("PRELUDE","repeat intro; try simp")
    work = Path(a.workdir).expanduser()
    outdir = work / "Batch"
    timeout = a.timeout

    # 対象ケース
    items=[]
    for gid,goal,style in bench:
        t = sanitize(preds.get(gid,""))
        if t and goal: items.append((gid,goal,t))
    tot = len(items)
    if a.limit>0: items = items[:a.limit]

    # チャンク分割
    B = max(1, a.batch)
    chunks=[items[i:i+B] for i in range(0,len(items),B)]

    ok=0; t0=time.perf_counter()
    for ci,chunk in enumerate(chunks, start=1):
        f = write_chunk(outdir, ci, chunk, prelude)
        t1=time.perf_counter()
        succ, log = run_lean(work, f, timeout=timeout)
        dt=time.perf_counter()-t1
        if succ:
            ok += len(chunk)
            print(f"[chunk {ci}/{len(chunks)}] ok={ok}/{tot}  file={f.name}  time={dt:.1f}s")
        else:
            print(f"[chunk {ci}] FAILED: {f.name}\n{os.linesep.join(log.splitlines()[-20:])}")
            print("Hint: このチャンクだけ個別検査してください：")
            print(f"      python -u -B ~/eval_success_lean4.py --bench {a.bench} --preds {a.preds} "
                  f"--workdir {a.workdir} --limit 0 --timeout {timeout}")
            break
    print(f"[done] success@1={ok}/{tot}={ok/tot if tot else 0:.3f} in {time.perf_counter()-t0:.1f}s")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--bench", required=True)
    ap.add_argument("--preds", required=True)
    ap.add_argument("--workdir", default=str(Path.home()/ "tactic_eval"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--batch", type=int, default=100)  # 1ファイルあたりの件数
    args=ap.parse_args(); main(args)

def sanitize(t: str) -> str:
    t = (t or '').strip()
    if t.endswith('.'): t = t[:-1]
    w = _first_word_token(t)
    w = CANON.get(w, w)
    return w

def sanitize(t: str) -> str:
    t = (t or '').strip()
    if t.endswith('.'): t = t[:-1]
    # ノイズ除去
    t = t.replace('\u200b','').replace('\ufeff','').replace('–','-').replace('—','-').replace('−','-')
    # 先頭を {"linarith","nlinarith","ring_nf","ring"} に強制クリップ
    m = HEAD_RE.match(t)
    if m: 
        return m.group(1)
    # バックアップ: 英数下線の最初の語を拾い、代表形に写像
    CANON = {
        "linarith":"linarith","lin":"linarith",
        "nlinarith":"nlinarith","nlin":"nlinarith",
        "ring_nf":"ring_nf","ringnf":"ring_nf",
        "ring":"ring"
    }
    m2 = _re.match(r'([A-Za-z_][A-Za-z0-9_]*)', t)
    w = (m2.group(1) if m2 else '').lower()
    return CANON.get(w, w)
