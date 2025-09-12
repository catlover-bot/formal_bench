#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, json, tempfile, time, subprocess
from pathlib import Path
from jinja2 import Template

def run_lean(code: str, lean_dir: Path, tpl_path: Path) -> tuple[bool, float, str]:
    tpl = Template(tpl_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "t.lean"
        f.write_text(code, encoding="utf-8")  # そのまま使う場合用
    t0 = time.perf_counter()
    p = subprocess.run(
        ["lake","env","lean","--quiet",str(f)],
        cwd=str(lean_dir),
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    return (p.returncode==0), (time.perf_counter()-t0), p.stdout

def render(tpl_path: Path, prop: str, proof_body: str) -> str:
    tpl = Template(tpl_path.read_text(encoding="utf-8"))
    return tpl.render(proposition=prop, proof="  " + proof_body.replace("\n","\n  "))

def try_tac(tpl_path: Path, lean_dir: Path, prop: str, tac: str) -> bool:
    code = render(tpl_path, prop, tac)
    ok, _, _ = run_lean(code, lean_dir, tpl_path)
    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)              # JSONL: {id, lean_prop, ...}
    ap.add_argument("--out_ok", required=True)            # OK（採用）
    ap.add_argument("--out_ng", required=True)            # NG（棄却、理由も書く）
    ap.add_argument("--lean-dir", required=True)
    ap.add_argument("--tpl", default="tools/wrap_by.lean.j2")
    ap.add_argument("--require", default="", help="comma; at least one must SOLVE")
    ap.add_argument("--reject",  default="trivial,simp,decide", help="comma; ALL must FAIL")
    args = ap.parse_args()

    lean_dir = Path(args.lean_dir).resolve()
    tpl_path = Path(args.tpl).resolve()
    req = [t.strip() for t in args.require.split(",") if t.strip()]
    rej = [t.strip() for t in args.reject.split(",") if t.strip()]

    n_total = n_ok = 0
    with open(args.input,"r",encoding="utf-8") as fin, \
         open(args.out_ok,"w",encoding="utf-8") as fok, \
         open(args.out_ng,"w",encoding="utf-8") as fng:
        for ln in fin:
            ln=ln.strip()
            if not ln: continue
            ex=json.loads(ln)
            n_total += 1
            prop = ex["lean_prop"]; _id = ex.get("id","?")
            # 1) reject が一つでも解けたら NG
            rejected = False
            for t in rej:
                if try_tac(tpl_path, lean_dir, prop, t):
                    fng.write(json.dumps({**ex,"_sieve":"reject:"+t}, ensure_ascii=False)+"\n")
                    rejected = True
                    break
            if rejected: continue
            # 2) require が空なら「rejectされなかった＝OK」扱い
            if not req:
                fok.write(json.dumps({**ex,"_sieve":"ok:noreq"}, ensure_ascii=False)+"\n")
                n_ok += 1
                continue
            # 3) require のいずれかで解ければ OK
            solved = False
            for t in req:
                if try_tac(tpl_path, lean_dir, prop, t):
                    fok.write(json.dumps({**ex,"_sieve":"ok:require:"+t}, ensure_ascii=False)+"\n")
                    solved = True
                    n_ok += 1
                    break
            if not solved:
                fng.write(json.dumps({**ex,"_sieve":"unsolved_by_require"}, ensure_ascii=False)+"\n")

    print(json.dumps({"total": n_total, "ok": n_ok, "ng": n_total-n_ok}, ensure_ascii=False))

if __name__ == "__main__":
    main()
