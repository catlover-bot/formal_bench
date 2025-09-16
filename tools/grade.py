#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lean whole-proof ベンチ用 採点スクリプト（ID/OOD + 質&効率 指標込み）
出力：Pass@k / QES / AUC@Time に加え、split別・(domain/style)別の集計
"""

import argparse
import json
import statistics
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Tuple, List, Dict, Any

import numpy as np
from jinja2 import Template
from tqdm import tqdm
import re
import shutil

# --- 解析用：axioms 抽出（#print axioms <name> の行を拾う） ---
# どの名前でも拾えるようにゆるめに
AXIOM_RE = re.compile(r'axioms\s+([A-Za-z0-9_\.]+)\s*:\s*(.*)', re.IGNORECASE)

# ---------------------------------------------------------------------
# Lean 実行ヘルパ
# ---------------------------------------------------------------------
def run_lean(tmp_lean: Path, lean_dir: Path) -> Tuple[bool, float, str]:
    """
    lake env lean で .lean をコンパイルして結果を返す
    :return: (success, seconds, stdout_text)
    """
    t0 = time.perf_counter()
    proc = subprocess.run(
        ["lake", "env", "lean", "--quiet", str(tmp_lean.resolve())],
        cwd=str(lean_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    dt = time.perf_counter() - t0
    return proc.returncode == 0, dt, proc.stdout


def _indent_two_spaces(s: str) -> str:
    return "\n".join(("  " + ln if ln.strip() else ln) for ln in s.splitlines())


def render_wrapper(tpl: Template, proposition: str, proof_body: str) -> str:
    """
    Jinja2 テンプレに命題と証明本文を差し込む。
    - テンプレ側が `by {{ proof }}` を想定しているケース（本文のみを入れる）
    - あるいは `{{ PROOF }}` を丸ごと入れるケース
    の両対応にするため、複数名で渡す。
    """
    return tpl.render(
        proposition=proposition,
        proof=_indent_two_spaces(proof_body),
        PROP=proposition,
        PROOF=proof_body,  # テンプレが「by」を含んでいない場合はこちらを使える
    )

# ---------------------------------------------------------------------
# 1問ぶんの採点：候補 k 本を順番に検証し、最初に通った時刻 t_success を記録
# ---------------------------------------------------------------------
def grade_item(
    example: Dict[str, Any], proofs: List[str], tpl: Template, lean_dir: Path
) -> Dict[str, Any]:
    """
    :param example: {"id", "lean_prop", ...}
    :param proofs:  候補証明の文字列リスト（長さ k）
    :return: 辞書（pass, t_success, kernel_time_med, proof_len_med_tok, axioms, axiom_penalty）
    """
    if "lean_prop" not in example:
        raise KeyError("example に 'lean_prop' がありません。命題は Prop 式で渡してください。")

    qid = example.get("id", "unknown")
    prop = example["lean_prop"]
    times: List[float] = []
    lens: List[int] = []
    used_axioms: set[str] = set()

    ok_any = False
    winner = None
    t_success: float | None = None
    t_cum = 0.0  # 候補を順番に検証して“通るまでの累積時間”を測る

    # 候補が空でも一応走らせる（ただし失敗になる）
    if not proofs:
        proofs = []

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)

        for i, p in enumerate(proofs):
            code = render_wrapper(tpl, prop, p)

            # 一時ファイルに書く
            f = td_path / "cand.lean"
            f.write_text(code, encoding="utf-8")

            # デバッグ用に保存
            out_dir = Path("out")
            out_dir.mkdir(exist_ok=True)
            (out_dir / "last.lean").write_text(code, encoding="utf-8")
            (out_dir / f"last_{qid}_{i}.lean").write_text(code, encoding="utf-8")

            ok, sec, out = run_lean(f, lean_dir)
            times.append(sec)
            lens.append(len(p.split()))
            t_cum += sec

            if ok and t_success is None:
                ok_any = True
                t_success = t_cum
                winner = p
                # axioms
                m = AXIOM_RE.search(out)
                if m:
                    for a in m.group(2).split(","):
                        a = a.strip()
                        if a:
                            used_axioms.add(a)
                # 最初に通ったら打ち切り（Pass@k と AUC の観点で早期終了）
                break

    # デフォルトのペナルティ（後で --constructive で強化可）
    uses_classical = any("Classical" in a for a in used_axioms)
    extra_axioms = len([a for a in used_axioms if "Classical" not in a])
    penalty = (1.0 if uses_classical else 0.0) + 0.5 * extra_axioms

    return {
        "pass": ok_any,
        "winner": (winner if ok_any else None),
        "t_success": t_success,  # None=失敗
        "kernel_time_med": statistics.median(times) if times else None,
        "proof_len_med_tok": statistics.median(lens) if lens else None,
        "axioms": sorted(used_axioms),
        "axiom_penalty": penalty,
    }

# ---------------------------------------------------------------------
# スカラー正規化（0..1）
# ---------------------------------------------------------------------
def normalize(vals: List[float]) -> float:
    if not vals:
        return 0.0
    v = np.array(vals, dtype=float)
    p95 = np.percentile(v, 95)
    v = np.clip(v, 0, p95)
    rng = v.max() - v.min()
    if rng <= 1e-9:
        return 0.0
    return float(((v - v.min()) / rng).mean())

def auc_mean(t_success_list: List[float | None], T: float) -> float:
    """AUC@Time = 平均 max(0, 1 - t_success/T)。失敗(None)は 0 扱い"""
    vals: List[float] = []
    T = max(T, 1e-9)
    for t in t_success_list:
        if t is None:
            vals.append(0.0)
        else:
            vals.append(max(0.0, 1.0 - (t / T)))
    return sum(vals) / max(len(vals), 1)

# ---------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="JSONL: 1行=1問（lean_prop 必須）")
    ap.add_argument("--preds", required=True, help="JSON: id -> [proof_1, ..., proof_k]")
    ap.add_argument("--out", required=True, help="結果JSONの出力パス")
    ap.add_argument("--k", type=int, default=32, help="各問題あたり採点する候補本数")
    ap.add_argument(
        "--lean-dir",
        default=str(Path(__file__).resolve().parents[1] / "lean"),
        help="`lakefile.lean` があるディレクトリ（mathlib環境）",
    )
    ap.add_argument(
        "--tpl",
        default=str(Path(__file__).resolve().parent / "wrapper_template.lean.j2"),
        help="Jinja2 テンプレートのパス",
    )
    ap.add_argument("--lambda1", type=float, default=0.20, help="QES: KernelTime 正規化の係数")
    ap.add_argument("--lambda2", type=float, default=0.10, help="QES: ProofLen 正規化の係数")
    ap.add_argument("--lambda3", type=float, default=0.15, help="QES: AxiomPenalty の係数")
    ap.add_argument("--aucT", type=float, default=5.0, help="AUC@Time のしきい秒 T")
    ap.add_argument(
        "--constructive",
        action="store_true",
        help="Constructive 重視のペナルティ（Classical=+2, 追加公理=+1）に切替",
    )
    ap.add_argument(
        "--ban_strong",
        action="store_true",
        help="ban strong tactics (nlinarith,aesop)",
    )
    args = ap.parse_args()

    lean_dir = Path(args.lean_dir).resolve()
    if not (lean_dir / "lakefile.lean").exists():
        raise SystemExit(f"[ERROR] lean-dir が lake プロジェクトではありません: {lean_dir}")

    tpl = Template(Path(args.tpl).read_text(encoding="utf-8"))
    preds: Dict[str, List[str]] = json.loads(Path(args.preds).read_text(encoding="utf-8"))

    # 集計用
    N = 0
    n_pass = 0
    times: List[float] = []
    lens: List[float] = []
    penalties: List[float] = []
    tsuccs: List[float | None] = []

    per_item: Dict[str, Any] = {}
    buckets: Dict[str, Dict[str, Any]] = {}

    # 強戦術の簡易フィルタ
    BANNED = ("nlinarith", "aesop")

    # JSONL 走査
    with open(args.input, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Grading", unit="item"):
            s = line.strip()
            if not s:
                continue
            ex = json.loads(s)
            qid = ex["id"]
            cands_all = preds.get(qid, []) or []
            cands = cands_all[: args.k]

            if args.ban_strong:
                cands = [c for c in cands if not any(b in c for b in BANNED)]

            # 採点（候補が空でも空で走らせて失敗扱い）
            res = grade_item(ex, cands, tpl, lean_dir)

            # Constructive ペナルティに切替
            if args.constructive:
                uses_classical = any("Classical" in a for a in res["axioms"])
                extra_axioms = len([a for a in res["axioms"] if "Classical" not in a])
                res["axiom_penalty"] = (2.0 if uses_classical else 0.0) + 1.0 * extra_axioms

            per_item[qid] = res

            # --- 全体集計 ---
            N += 1
            n_pass += int(res["pass"])
            if res["kernel_time_med"] is not None:
                times.append(float(res["kernel_time_med"]))
            if res["proof_len_med_tok"] is not None:
                lens.append(float(res["proof_len_med_tok"]))
            penalties.append(float(res["axiom_penalty"]))
            tsuccs.append(res["t_success"])

            # --- 分割集計（split / domain-style） ---
            split = ex.get("split", "id")
            domain = ex.get("domain", "?")
            style = ex.get("style", "?")
            keys = [f"split::{split}", f"ds::{domain}/{style}"]
            for key in keys:
                b = buckets.setdefault(key, {"N": 0, "pass": 0, "tsucc": []})
                b["N"] += 1
                b["pass"] += int(res["pass"])
                b["tsucc"].append(res["t_success"])

    # --- 指標計算 ---
    pass_k = n_pass / max(N, 1)
    t_norm = normalize(times)
    l_norm = normalize(lens)
    ax_norm = sum(penalties) / max(N, 1)
    QES = pass_k - args.lambda1 * t_norm - args.lambda2 * l_norm - args.lambda3 * ax_norm
    AUC = auc_mean(tsuccs, args.aucT)

    split_report: Dict[str, Any] = {}
    for key, b in buckets.items():
        split_report[key] = {
            "N": b["N"],
            "Pass@k": b["pass"] / max(b["N"], 1),
            "AUC@Time": auc_mean(b["tsucc"], args.aucT),
        }

    # 出力
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "Pass@k": pass_k,
        "QES": QES,
        "AUC@Time": AUC,
        "KernelTime_norm": t_norm,
        "ProofLen_norm": l_norm,
        "AxiomPenalty_avg": ax_norm,
        "by_split_or_domain_style": split_report,
        "items": per_item,
        "meta": {
            "k": args.k,
            "aucT": args.aucT,
            "lambda": {"t": args.lambda1, "len": args.lambda2, "ax": args.lambda3},
            "constructive": bool(args.constructive),
            "lean_dir": str(lean_dir),
            "tpl": str(args.tpl),
            "ban_strong": bool(args.ban_strong),
        },
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # コンソールは要点だけ
    print(json.dumps({"Pass@k": pass_k, "QES": QES, "AUC@Time": AUC}, ensure_ascii=False))


if __name__ == "__main__":
    main()
