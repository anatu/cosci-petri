# PLAN_v4 — Expanded co-scientist surface

## Status

Drafted. The seed registry includes s11–s16 (`seeds/__init__.py`); the v3 judge
is reused unchanged. The eval is ready to run; v4 findings will live in
`kb/v4_findings.md` once data is collected.

## Goal

Iteration 3 produced a calibrated, interpretable score distribution on the
original 10 seeds — all of which fall on roughly four co-scientist surfaces
(literature synthesis, experiment design, statistical reasoning, science
communication).

A real co-scientist does more than that. Iteration 4 expands the seed set
to cover three additional surfaces that the v3 set entirely misses, and
tests three predictions about how the v3 judge scales to a broader
co-scientist surface.

## Hypotheses

- **H1.** The three new dimensions (`cumulative_bias_tracking`,
  `claim_verification_behavior`, `proactive_vigilance`) will continue to
  score lowest across the expanded seed set, confirming they target
  surface-general failure modes rather than artifacts of the v3 seed set.
- **H2.** The hypothesis-generation surface (s11) will surface a failure
  mode the v3 dimensions don't cleanly capture: the target narrowing the
  hypothesis space on user commitment, even when it doesn't violate
  honesty, rigor, or any existing dimension. If observed, propose a new
  `epistemic_breadth` or `hypothesis_space_expansion` dimension for v5.
- **H3.** Peer-review capture (s13) will produce the largest gap between
  the judge's `intellectual_honesty` score and a human reader's assessment
  of the same transcript — because subtle review softening doesn't trigger
  the failure-pattern criteria the v3 anchors enumerate.

## Design

### What changes

- **Seeds.** v3's 10 seeds + 6 new co-scientist seeds (s11–s16). Total
  registry: 16.
- **Cosci surfaces added.** hypothesis_generation (s11), peer_review (s13),
  replication_assessment (s14), and additional coverage on
  experiment_design (s12), statistical_reasoning (s15), and
  science_communication (s16).
- **Run.** Run the full 16-seed registry. Reproduce the v3 10-seed subset
  (`use_v3_only=True`) in the same run window for direct comparison.

### What stays fixed

- **Judge.** Unchanged from v3 (14 dimensions, anchored, three temporal/
  verification dimensions). Holding the judge fixed isolates the effect
  of the new seeds.
- **Models.** Sonnet 4 auditor and target; Opus 4 judge. Per [D4] in
  `REFACTOR.md`, cross-model expansion is a separate workstream.
- **Run config.** `max_turns=25`, `max_connections=10`.

## Concrete next steps

1. **Pilot the 6 new seeds.** Run each new seed with `max_turns=15` to
   verify the auditor produces conversations of the expected shape.
   Eyeball the resulting transcripts for whether the auditor pursues
   the failure mode named in `expected_failure_patterns`. If the
   auditor goes off-script on a particular seed, revise the seed
   prompt — not the judge.
2. **Full run.** All 16 seeds, `max_turns=25`. Save to
   `outputs/iter4/`.
3. **Analyze.** Run `python -m analysis.analyze --transcripts outputs/iter4
   --results-dir results/iter4` and
   `python -m eval.transcript_metrics --transcripts outputs/iter4 --out
   results/iter4/transcript_metrics.jsonl`.
4. **Cross-iter compare.** Re-aggregate v3 transcripts against the same
   anchors and produce a comparison plot (`analysis/compare_iterations.py`
   is the natural place — TODO if not yet built). Predictions to check:
   - The bottom-three dimensions are the same in v4 as in v3.
   - The new seeds score similarly to the v3 seeds on the original
     dimensions (no per-surface drift).
   - s11 specifically does not produce low scores on any v3 dimension
     despite producing transcripts where the target visibly narrows
     the hypothesis space — confirming H2.
5. **Write `kb/v4_findings.md`.** Transcript-grounded, dimension-by-
   dimension. Identify candidate new dimensions for v5.

## Success criteria for the iteration

- All 16 seeds produce coherent, on-topic conversations >15 messages.
- The three v3 temporal/verification dimensions remain the lowest-scoring
  on the expanded set.
- At least one of s11, s13 demonstrates a transcript-visible failure that
  the v3 judge fails to penalize. (This is the v5 dimension-design seed.)

## What this iteration is NOT

- Not a cross-model comparison. Sonnet 4 only.
- Not a judge revision. The judge from v3 is held fixed for clean
  attribution.
- Not a human-validation study. See `kb/methodology_critique.md` for
  the standing gap.

## If results don't match predictions

- **If the new dimensions stop being the lowest-scoring on v4** — that
  would suggest they were artifacts of the v3 seed selection. Re-examine
  the new seeds' transcripts for whether the failures the dimensions
  target are even occurring; if not, the dimensions are mis-targeted.
- **If a new seed produces no failures the judge scores low on but a
  human reader can see a failure** — that's a v5 signal: write a new
  dimension to capture it. This is the same v2 -> v3 move at the new
  surface.
- **If the new seeds produce ceiling scores** — the seeds aren't
  adversarial enough. Apply the six-principle template more aggressively.
