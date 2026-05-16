"""
Aggregate per-dimension scores from Petri transcripts.

A Petri transcript is a JSON file with structure:

    {
      "metadata": {
        "transcript_id": "...",
        "auditor_model": "...",
        "target_model": "...",
        "seed_instruction": "...",
        "judge_output": {
          "scores": { "<dim_name>": <int 1..10>, ... },
          "justification": "...",
          ...
        }
      },
      "messages": [...],
      "target_messages": [...]
    }

This module loads a directory of transcripts, joins them to the seed registry,
and produces:

- a per-dimension mean ± stderr table
- a per-seed × per-dimension heatmap
- a conversation-length histogram

Usage:
    python -m analysis.analyze --transcripts outputs/research-assistant-audit \
                               --results-dir results/iter3
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def load_transcripts(directory: Path) -> list[dict]:
    """Load all transcript JSON files from a directory (recursive)."""
    transcripts: list[dict] = []
    for path in sorted(directory.rglob("transcript_*.json")):
        try:
            with path.open() as f:
                d = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"  skipped {path.name}: {e}", file=sys.stderr)
            continue
        d["_source_path"] = str(path)
        transcripts.append(d)
    return transcripts


def extract_scores(transcripts: Iterable[dict]) -> list[dict]:
    """One row per transcript with seed id (if recoverable), scores, length.

    Seed id matching is best-effort. Older transcripts (pre-refactor) saved
    only `seed_instruction` text, not a structured id; we match by prefix
    against the registered seed prompts.
    """
    from seeds import SEED_REGISTRY

    seed_by_prefix = {s.prompt.strip()[:80]: s.id for s in SEED_REGISTRY}

    rows: list[dict] = []
    for t in transcripts:
        meta = t.get("metadata", {})
        jo = meta.get("judge_output") or {}
        scores = jo.get("scores") if isinstance(jo, dict) else None
        if not scores:
            continue
        instruction = (meta.get("seed_instruction") or "").strip()
        seed_id = seed_by_prefix.get(instruction[:80], None)
        rows.append({
            "transcript_id": meta.get("transcript_id"),
            "auditor_model": meta.get("auditor_model"),
            "target_model": meta.get("target_model"),
            "seed_id": seed_id,
            "seed_instruction_head": instruction[:60],
            "scores": scores,
            "n_messages": len(t.get("messages") or []),
            "n_target_messages": len(t.get("target_messages") or []),
            "source": t.get("_source_path"),
        })
    return rows


def per_dimension_stats(rows: list[dict]) -> dict[str, dict[str, float]]:
    """Mean, stderr, n per dimension across all transcripts."""
    by_dim: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        for k, v in r["scores"].items():
            if isinstance(v, (int, float)):
                by_dim[k].append(float(v))
    stats = {}
    for dim, values in by_dim.items():
        n = len(values)
        m = mean(values) if n else 0.0
        sd = stdev(values) if n > 1 else 0.0
        se = sd / (n ** 0.5) if n > 1 else 0.0
        stats[dim] = {"mean": m, "stderr": se, "n": n}
    return stats


def heatmap_table(rows: list[dict]) -> dict[str, dict[str, float]]:
    """seed_id -> dim -> score (averaged if multiple transcripts per seed)."""
    bucket: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        sid = r["seed_id"] or "(unmatched)"
        for k, v in r["scores"].items():
            if isinstance(v, (int, float)):
                bucket[sid][k].append(float(v))
    return {
        sid: {dim: mean(vals) for dim, vals in dims.items()}
        for sid, dims in bucket.items()
    }


def render_table(stats: dict[str, dict[str, float]]) -> str:
    """ASCII table of per-dimension means and stderrs, sorted by mean asc."""
    items = sorted(stats.items(), key=lambda kv: kv[1]["mean"])
    width = max((len(k) for k in stats), default=10)
    lines = [
        f"{'dimension'.ljust(width)}  {'mean':>6}  {'stderr':>7}  {'n':>4}",
        f"{'-' * width}  {'-' * 6}  {'-' * 7}  {'-' * 4}",
    ]
    for dim, s in items:
        lines.append(
            f"{dim.ljust(width)}  {s['mean']:6.2f}  {s['stderr']:7.3f}  {s['n']:4d}"
        )
    return "\n".join(lines)


def write_plots(
    rows: list[dict],
    stats: dict[str, dict[str, float]],
    heatmap: dict[str, dict[str, float]],
    out_dir: Path,
) -> None:
    """Write per-dimension bar chart, heatmap, and length histogram to out_dir."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as e:
        print(f"  matplotlib unavailable, skipping plots: {e}", file=sys.stderr)
        return

    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Per-dimension means with stderr error bars
    items = sorted(stats.items(), key=lambda kv: kv[1]["mean"])
    dims = [k for k, _ in items]
    means = [v["mean"] for _, v in items]
    errs = [v["stderr"] for _, v in items]
    fig, ax = plt.subplots(figsize=(10, max(4, len(dims) * 0.35)))
    ax.barh(dims, means, xerr=errs, color="#4A90E2", ecolor="#222")
    ax.set_xlabel("mean score (1–10)")
    ax.set_xlim(0, 10)
    ax.set_title("Per-dimension means")
    fig.tight_layout()
    fig.savefig(out_dir / "per_dimension_means.png", dpi=150)
    plt.close(fig)

    # 2. Heatmap (seed × dimension)
    seeds = sorted(heatmap.keys())
    all_dims = sorted({d for s in heatmap.values() for d in s.keys()})
    M = np.zeros((len(seeds), len(all_dims)))
    for i, s in enumerate(seeds):
        for j, d in enumerate(all_dims):
            M[i, j] = heatmap[s].get(d, np.nan)
    fig, ax = plt.subplots(figsize=(max(6, 0.4 * len(all_dims)), max(3, 0.4 * len(seeds))))
    im = ax.imshow(M, aspect="auto", cmap="RdYlGn", vmin=1, vmax=10)
    ax.set_xticks(range(len(all_dims)))
    ax.set_xticklabels(all_dims, rotation=60, ha="right", fontsize=8)
    ax.set_yticks(range(len(seeds)))
    ax.set_yticklabels(seeds, fontsize=8)
    fig.colorbar(im, ax=ax, label="score")
    ax.set_title("Per-seed × per-dimension scores")
    fig.tight_layout()
    fig.savefig(out_dir / "seed_dimension_heatmap.png", dpi=150)
    plt.close(fig)

    # 3. Conversation-length histogram
    lengths = [r["n_messages"] for r in rows if r["n_messages"]]
    if lengths:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(lengths, bins=min(20, max(5, len(lengths) // 2)), color="#7B68EE")
        ax.set_xlabel("messages per transcript")
        ax.set_ylabel("count")
        ax.set_title(f"Conversation-length distribution (n={len(lengths)})")
        fig.tight_layout()
        fig.savefig(out_dir / "conversation_length.png", dpi=150)
        plt.close(fig)


def write_json(rows: list[dict], stats: dict, heatmap: dict, out_dir: Path) -> None:
    """Persist machine-readable aggregates for cross-iter comparison."""
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "scores_per_transcript.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with (out_dir / "per_dimension_stats.json").open("w") as f:
        json.dump(stats, f, indent=2)
    with (out_dir / "seed_dimension_heatmap.json").open("w") as f:
        json.dump(heatmap, f, indent=2)


def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze a directory of Petri transcripts.")
    ap.add_argument(
        "--transcripts", type=Path, default=Path("outputs/research-assistant-audit"),
        help="Directory containing transcript_*.json files (searched recursively)",
    )
    ap.add_argument(
        "--results-dir", type=Path, default=Path("results/current"),
        help="Where to write aggregates and plots",
    )
    args = ap.parse_args()

    transcripts = load_transcripts(args.transcripts)
    print(f"Loaded {len(transcripts)} transcript(s) from {args.transcripts}")
    rows = extract_scores(transcripts)
    print(f"Extracted scores from {len(rows)} transcript(s) with judge_output")
    if not rows:
        print("No scored transcripts — nothing to aggregate.")
        return

    stats = per_dimension_stats(rows)
    heatmap = heatmap_table(rows)

    print()
    print(render_table(stats))
    print()

    write_plots(rows, stats, heatmap, args.results_dir / "plots")
    write_json(rows, stats, heatmap, args.results_dir)
    print(f"Wrote aggregates and plots to {args.results_dir}/")


if __name__ == "__main__":
    main()
