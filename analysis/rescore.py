"""
Re-score a saved Inspect AI eval log with the v3 judge anchors, using the
Anthropic API for the judge model. Workaround for sporadic `claudecode/`
judge parse failures (e.g. v4's s07 catastrophic all-1s sentinel).

Usage:
    python -m analysis.rescore \
        --log logs/2026-05-17T12-45-23-00-00_cosci-audit_bMa2RoedQvZe2xn3mfXeS3.eval \
        --output logs/v4_rescored.eval \
        --judge anthropic/claude-opus-4-20250514

After this runs, regenerate aggregates with `analysis.analyze` against the
saved transcripts directory; the .eval log itself is the source of truth for
scores. If you need updated `outputs/iter4/full/transcript_*.json` files,
extract them from the new log (see TODO at bottom).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from inspect_ai import score
from inspect_ai.log import read_eval_log, write_eval_log

from petri.scorers.judge import alignment_judge

from judge.rubrics import build_rubric_dict


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", type=Path, required=True, help="Input .eval log")
    ap.add_argument("--output", type=Path, required=True, help="Where to write rescored .eval")
    ap.add_argument(
        "--judge",
        type=str,
        default="anthropic/claude-opus-4-20250514",
        help="Judge model identifier (default: anthropic/claude-opus-4)",
    )
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument(
        "--only-samples",
        type=str,
        default=None,
        help=(
            "Comma-separated sample IDs to re-score. If set, the rest of the "
            "log is preserved unchanged. Useful for recovering specific "
            "parse-failure transcripts (e.g. --only-samples s07_sunk_cost_compliance)."
        ),
    )
    args = ap.parse_args()

    print(f"Reading log: {args.log}")
    log = read_eval_log(str(args.log), header_only=False)
    n_samples = len(log.samples) if log.samples else 0
    print(f"Samples: {n_samples}")

    only_set = set(args.only_samples.split(",")) if args.only_samples else None
    if only_set:
        targets = [s for s in log.samples if s.id in only_set]
        if not targets:
            print(f"No samples matched {only_set!r}; nothing to do.")
            return
        print(f"Re-scoring {len(targets)} of {n_samples} samples: {[t.id for t in targets]}")

    print(f"Building scorer with judge model: {args.judge}")
    scorer = alignment_judge(
        dimensions=build_rubric_dict(),
        model=args.judge,
        retries=args.retries,
    )

    if only_set:
        # Build a single-sample-subset log, score it, then splice scores back.
        original_samples = log.samples
        log.samples = targets
        rescored = score(log, scorers=scorer, action="overwrite")
        # Splice rescored sample objects back into the original ordering.
        rescored_by_id = {s.id: s for s in rescored.samples}
        merged = []
        for s in original_samples:
            merged.append(rescored_by_id.get(s.id, s))
        rescored.samples = merged
    else:
        print("Re-scoring all samples (overwrites existing scores)...")
        rescored = score(log, scorers=scorer, action="overwrite")

    print(f"Writing: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_eval_log(rescored, str(args.output))
    print("Done.")


if __name__ == "__main__":
    main()
