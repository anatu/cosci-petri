---
name: run-iteration
description: Orchestrate a full audit iteration — snapshot current config, run, save to results/iterN, draft kb/vN_findings.md.
---

# run-iteration — execute a full audit cycle

Use when running a new iteration end-to-end. The output is a self-contained
`results/iterN/` directory and a draft `kb/vN_findings.md`.

## Preconditions

- A `plans/PLAN_vN.md` exists and is committed. The iteration must have an
  explicit hypothesis and success criteria; don't run without them.
- The model, seed, and judge config in `config.py`, `seeds/`, and
  `judge/dimensions.py` matches what the plan describes.
- `.env` has `ANTHROPIC_API_KEY` set.

## Procedure

1. **Determine the iteration number.** Look at the highest N in
   `plans/PLAN_v*.md` and `kb/v*_findings.md`. The next iteration is N+1
   only if PLAN_vN exists and findings_vN is being drafted.

2. **Snapshot the config.** Before running, copy:
   - `seeds/` → `results/iterN/snapshot_seeds.json`
     (dump the SEED_REGISTRY's metadata via `[s.as_metadata() for s in
     SEED_REGISTRY]`).
   - `judge/dimensions.py` → `results/iterN/snapshot_judge.json`
     (dump the rendered rubric dict via `build_rubric_dict()`).
   This makes the iteration reproducible even if the live config moves on.

3. **Pilot.** Run 2 seeds with `max_turns=15` to validate setup:
   ```bash
   inspect eval ra_audit.py@cosci_audit \
     --model-role auditor=... --model-role target=... --model-role judge=... \
     -T max_turns=15 -T transcript_save_dir=./outputs/iterN/pilot \
     --limit 2
   ```
   Eyeball the pilot transcripts. Stop and revise if they look pathological.

4. **Full run.** All registered seeds at production `max_turns`:
   ```bash
   python -m eval.run_audit
   ```
   (Or the equivalent inspect CLI invocation pointed at
   `outputs/iterN/full`.)

5. **Aggregate.**
   ```bash
   python -m analysis.analyze --transcripts outputs/iterN/full --results-dir results/iterN
   python -m eval.transcript_metrics --transcripts outputs/iterN/full --out results/iterN/transcript_metrics.jsonl
   ```

6. **Cross-iter compare.** If a prior iteration's `results/iter(N-1)/`
   exists, produce a comparison plot — at minimum, a side-by-side bar
   chart of per-dimension means.

7. **Draft `kb/vN_findings.md`.** Use the prior `kb/vM_findings.md` files
   as the template. Required sections:
   - **Headline result.** One paragraph.
   - **Score table.** Cross-iter where possible.
   - **What transcript analysis revealed.** Per-seed walk-through with
     evidence cites.
   - **What the iteration confirmed / did NOT establish.** Explicitly
     name the gaps; don't oversell.

8. **Update the index.** Add a one-line link to the new findings doc in
   `README.md` if it lists per-iter findings, and append a brief note
   to `FINDINGS.md` if the headline result changes the standing
   conclusions.

## Don't

- Don't run an iteration without a written plan. The plan is the
  hypothesis you're testing; without it you cannot honestly say whether
  the iteration succeeded.
- Don't conflate seed changes and judge changes in the same iteration.
  One change at a time keeps attribution clean (this is the v1 -> v2 ->
  v3 lesson).
- Don't tune anchors or seeds post-hoc to make scores look better.
  Anchors/seeds are the IV; scores are the DV.
