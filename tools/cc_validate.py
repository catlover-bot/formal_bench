#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, subprocess, tempfile, time
from pathlib import Path

PALETTE = []

WRAP = """import Mathlib
import Aesop
set_option linter.docPrime false
namespace CC
def goalProp : Prop := {PROP}
theorem Proof : goalProp := by
  first
    | trivial
    | simp_all
    | simp
    | norm_num
    | aesop
    | linarith
    | nlinarith
    | ring
    | decide
#check Proof
end CC
"""

def try_one(prop:str, lean_dir:Path):
    import tempfile, subprocess, time
    with tempfile.TemporaryDirectory() as td:
        code = WRAP.replace("{PROP}", prop)
        f = Path(td)/"t.lean"; f.write_text(code, encoding="utf-8")
        t0=time.perf_counter()
        p = subprocess.run(["lake","env","lean","--quiet",str(f)],
            cwd=lean_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        dt=time.perf_counter()-t0
        return (p.returncode==0), ("first"), dt


def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out_ok", default="data/validated.jsonl")
    ap.add_argument("--out_ng", default="data/rejects.jsonl")
    ap.add_argument("--lean-dir", default=str(Path(__file__).resolve().parents[1]/"lean"))
    args=ap.parse_args()

    okf=open(args.out_ok,"w",encoding="utf-8"); ngf=open(args.out_ng,"w",encoding="utf-8")
    n_ok=n_ng=0
    for ln in open(args.input,"r",encoding="utf-8"):
        ex=json.loads(ln); prop=ex["lean_prop"]
        ok,tac,dt = try_one(prop, Path(args.lean_dir))
        ex["cc_ok"]=ok; ex["cc_tactic"]=tac; ex["cc_time"]=dt
        if ok:
            okf.write(json.dumps(ex,ensure_ascii=False)+"\n"); n_ok+=1
        else:
            ngf.write(json.dumps(ex,ensure_ascii=False)+"\n"); n_ng+=1
    okf.close(); ngf.close()
    print(json.dumps({"ok":n_ok,"reject":n_ng},ensure_ascii=False))

if __name__=="__main__":
    main()
