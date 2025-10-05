# formal_bench

## Benchmark v0.4
- File: `benchmarks/bench_v0_4.jsonl`
- Meta: `benchmarks/bench_v0_4.meta.json`  （items=600, sha256=c054cf5f3db2af6f2c1b8c8e62b05e7e7ca5d2f2202857eb037a6e65aa862f4f）

## What is this?
Formal proof–style tasks for LLMs, evaluated by **Lean 4 execution** (`success@1`) with an optional **gate + style canonicalization** step to make predictions robust to formatting variations.

**Contents**
- `benchmarks/` — JSONL benchmark (v0.4) and meta
- `results/<run-id>/` — aggregated CSVs (`final_table.csv`, `summary.csv`, `ring_stats.csv`, `length_stats.csv`)
- `scripts/` — helper scripts (`canonize_pred.py`, `canonize_pred_with_style.py`, `eval_success_lean4_chunked.py`, `summarize_runs.py`)
- `environment.yml` — minimal Python deps for the scripts (Lean itself is installed separately)

---

## Quick start (evaluate existing predictions with Lean)
Assume you already have a predictions file like `*_stylecanon.json`.

```bash
conda env create -f environment.yml
conda activate formal-bench

python scripts/eval_success_lean4_chunked.py \
  --bench benchmarks/bench_v0_4.jsonl \
  --preds /path/to/your_model_gate_stylecanon.json \
  --workdir . --batch 100 --timeout 1200
```

```bash
python scripts/eval_success_lean4_chunked.py \
  --bench benchmarks/bench_v0_4.jsonl \
  --preds results/20251001_192544_v100/qwen25_7b_gate_stylecanon.json \
  --workdir lean --batch 100 --timeout 1200
```
