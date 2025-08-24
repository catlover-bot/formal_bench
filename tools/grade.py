from __future__ import annotations
#!/usr/bin/env python3
import argparse, json, subprocess, tempfile, time, statistics, re
from pathlib import Path
from typing import Tuple
from jinja2 import Template

AXIOM_RE = re.compile(r'axioms\s+Bench\.CandidateProof\s*:\s*(.*)', re.IGNORECASE)

def run_lean(tmp_lean: Path, lean_dir: Path) -> Tuple[bool, float, str]:
    t0 = time.perf_counter()
    proc = subprocess.run(
        ["lake", "env", "lean", "--quiet", str(tmp_lean)],
        cwd=lean_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    return proc.returncode == 0, time.perf_counter()-t0, proc.stdout

def render_wrapper(tpl: Template, proposition: str, proof: str) -> str:
    # proof は `by` なしのタクティク本文でもOK（テンプレ側で by を付けている）
    body = "\n".join("  " + ln if ln.strip() else ln for ln in proof.splitlines())
    return tpl.render(proposition=proposition, proof=body)

def grade_item(example, proofs, tpl: Template, lean_dir: Path):
    prop = example["lean_prop"]
    times, ok_any, used_axioms, lens = [], False, set(), []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for p in proofs:
            code = render_wrapper(tpl, prop, p)
            f = td / "cand.lean"
            f.write_text(code, encoding="utf-8")
            ok, sec, out = run_lean(f, lean_dir)
            times.append(sec); lens.append(len(p.split()))
            if ok: ok_any = True
            m = AXIOM_RE.search(out)
            if m:
                used_axioms.update(a.strip() for a in m.group(1).split(",") if a.strip())
    # 例：Classical依存=+1, 追加公理ごと+0.5（初期案）
    cls = any("Classical" in a for a in used_axioms)
    extra = len([a for a in used_axioms if "Classical" not in a])
    penalty = (1.0 if cls else 0.0) + 0.5*extra
    return {
        "pass": ok_any,
        "kernel_time_med": statistics.median(times) if times else None,
        "proof_len_med_tok": statistics.median(lens) if lens else None,
        "axioms": sorted(used_axioms),
        "axiom_penalty": penalty
    }

def normalize(vals):
    if not vals: return 0.0
    import numpy as np
    v = np.array(vals, float)
    p95 = np.percentile(v, 95)
    v = np.clip(v, 0, p95)
    v = (v - v.min()) / (v.max() - v.min() + 1e-9)
    return float(v.mean())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--preds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=32)
    ap.add_argument("--lean-dir", default=str(Path(__file__).resolve().parents[1] / "lean"))
    ap.add_argument("--tpl", default=str(Path(__file__).resolve().parent / "wrapper_template.lean.j2"))
    ap.add_argument("--lambda1", type=float, default=0.20)  # KernelTime
    ap.add_argument("--lambda2", type=float, default=0.10)  # ProofLen
    ap.add_argument("--lambda3", type=float, default=0.15)  # AxiomPenalty
    args = ap.parse_args()

    tpl = Template(Path(args.tpl).read_text(encoding="utf-8"))
    preds = json.loads(Path(args.preds).read_text(encoding="utf-8"))

    N = n_pass = 0
    times, lens, penalties = [], [], []
    per_item = {}
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            ex = json.loads(line)
            qid = ex["id"]; cand = preds.get(qid, [])[:args.k]
            res = grade_item(ex, cand, tpl, Path(args.lean_dir if hasattr(args, 'lean-dir') else args.lean_dir))
            per_item[qid] = res
            N += 1; n_pass += int(res["pass"])
            if res["kernel_time_med"] is not None: times.append(res["kernel_time_med"])
            if res["proof_len_med_tok"] is not None: lens.append(res["proof_len_med_tok"])
            penalties.append(res["axiom_penalty"])

    pass_k = n_pass / max(N, 1)
    t_norm, l_norm = normalize(times), normalize(lens)
    ax_norm = sum(penalties)/max(N,1)
    QES = pass_k - args.lambda1*t_norm - args.lambda2*l_norm - args.lambda3*ax_norm

    report = {"Pass@k": pass_k, "QES": QES,
              "KernelTime_norm": t_norm, "ProofLen_norm": l_norm,
              "AxiomPenalty_avg": ax_norm, "items": per_item}
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"Pass@k": pass_k, "QES": QES}, ensure_ascii=False))

if __name__ == "__main__":
    main()
