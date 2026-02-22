import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path

HEAD_RE = re.compile(r"^(linarith|nlinarith|ring_nf|ring)\b", re.I)
CANON = {
    "linarith": "linarith",
    "lin": "linarith",
    "nlinarith": "nlinarith",
    "nlin": "nlinarith",
    "ring_nf": "ring_nf",
    "ringnf": "ring_nf",
    "ring": "ring",
}

HDR = """\
import Mathlib
set_option autoImplicit false
set_option maxRecDepth 10000
set_option maxHeartbeats 200000
"""


def _first_word_token(text: str) -> str:
    text = (text or "").strip()
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = text.replace("窶・", "-").replace("竏・", "-")
    m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)", text)
    return m.group(1).lower() if m else ""


def sanitize(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    if text.endswith("."):
        text = text[:-1]

    normalized = text.replace("\u200b", "").replace("\ufeff", "")
    m = HEAD_RE.match(normalized)
    if m:
        return m.group(1).lower()

    token = _first_word_token(normalized)
    return CANON.get(token, token)


def load_bench(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            goal = item.get("lean_prop") or item.get("goal") or item.get("statement") or ""
            rows.append((item.get("id", ""), goal, item.get("style", "")))
    return rows


def load_preds(path):
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)
    return {k: (v[0] if isinstance(v, list) and v else "") for k, v in obj.items()}


def write_chunk(root: Path, chunk_id: int, cases, prelude: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"Batch_{chunk_id:03d}.lean"
    lines = [HDR, ""]
    for i, (gid, goal, tactic) in enumerate(cases):
        theorem = f"""\
/-- {gid} -/
theorem _case_{chunk_id:03d}_{i:03d} : {goal} := by
  {prelude}
  {tactic}
"""
        lines.append(theorem)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def run_lean(workdir: Path, lean_file: Path, timeout: int):
    result = subprocess.run(
        ["lake", "env", "lean", str(lean_file)],
        cwd=str(workdir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return result.returncode == 0, result.stdout.decode("utf-8", "ignore")


def main(args):
    bench = load_bench(args.bench)
    preds = load_preds(args.preds)
    prelude = os.environ.get("PRELUDE", "repeat intro; try simp")
    workdir = Path(args.workdir).expanduser()
    chunk_dir = workdir / "Batch"

    items = []
    for gid, goal, _style in bench:
        tactic = sanitize(preds.get(gid, ""))
        if tactic and goal:
            items.append((gid, goal, tactic))

    if args.limit > 0:
        items = items[: args.limit]

    total = len(items)
    batch_size = max(1, args.batch)
    chunks = [items[i : i + batch_size] for i in range(0, total, batch_size)]

    ok = 0
    started = time.perf_counter()

    for chunk_idx, chunk in enumerate(chunks, start=1):
        lean_file = write_chunk(chunk_dir, chunk_idx, chunk, prelude)
        t1 = time.perf_counter()
        success, log = run_lean(workdir, lean_file, timeout=args.timeout)
        elapsed = time.perf_counter() - t1

        if success:
            ok += len(chunk)
            print(
                f"[chunk {chunk_idx}/{len(chunks)}] ok={ok}/{total} "
                f"file={lean_file.name} time={elapsed:.1f}s"
            )
            continue

        tail = os.linesep.join(log.splitlines()[-20:])
        print(f"[chunk {chunk_idx}] FAILED: {lean_file.name}\n{tail}")
        print("Hint: rerun with a smaller --batch (e.g. 1) to isolate the failing case.")
        print(
            f"      python scripts/eval_success_lean4_chunked.py --bench {args.bench} "
            f"--preds {args.preds} --workdir {args.workdir} --batch 1 --timeout {args.timeout}"
        )
        break

    total_elapsed = time.perf_counter() - started
    rate = (ok / total) if total else 0.0
    print(f"[done] success@1={ok}/{total}={rate:.3f} in {total_elapsed:.1f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate tactic-head predictions with Lean 4 in chunked batches."
    )
    parser.add_argument("--bench", required=True, help="Benchmark JSONL file.")
    parser.add_argument("--preds", required=True, help="Predictions JSON file.")
    parser.add_argument(
        "--workdir",
        default=str(Path.home() / "tactic_eval"),
        help="Lean/Lake working directory (typically ./lean).",
    )
    parser.add_argument("--limit", type=int, default=0, help="Optional item limit (0 = all).")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout per chunk (seconds).")
    parser.add_argument("--batch", type=int, default=100, help="Cases per generated Lean file.")
    main(parser.parse_args())
