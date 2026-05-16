# PLAN_v1 — Baseline audit (canonical failure modes)

## Status

Executed. Findings in `kb/v1_findings.md`.

## Goal

Stand up a working Petri v2 evaluation that tests whether Claude Sonnet 4 fails at
the canonical research-assistant failure modes documented in the literature:
hallucinated citations, sycophancy under social pressure, correlation-vs-causation
confusion, scope mismanagement, and basic statistical reasoning errors.

Calibrate expectations against the Petri infrastructure (auditor / target / judge
loop) before iterating on either the seeds or the judge.

## Hypotheses

- **H1.** A Sonnet-4 target will fail at the same failure modes that older models
  failed at: it will accept fabricated citations, defer to confident expert
  pushback, and produce one-sided syntheses when the user appears expert.
- **H2.** A 14-dimension judge with descriptive (un-anchored) rubric prompts will
  produce per-dimension scores with enough variance to separate stronger from
  weaker target behaviors.
- **H3.** The default Petri auditor agent will produce conversations long enough
  (>15 messages) for subtle multi-turn failures to develop.

## Design

- **Models.** Auditor = Sonnet 4. Target = Sonnet 4. Judge = Opus 4.
- **Seeds.** 10 seed instructions, each framing the auditor as a researcher
  testing a single canonical failure mode (hallucination, deference, etc.).
  Each seed is a free-form string passed as the `Sample.input`.
- **Judge.** Custom `dimensions` dict overriding the Petri default alignment
  dimensions, scoring 1–10 with a one-sentence description per dimension.
- **Run.** `max_turns=25`, `max_connections=10`, `fail_on_error=3`,
  transcripts saved to `outputs/research-assistant-audit/`.

## Success criteria for the iteration

- All 10 seeds complete without infra errors.
- Score distribution shows variance across both seeds and dimensions (stderr > ~1
  on at least half the dimensions).
- Qualitative read of transcripts confirms the target exhibited at least 2–3 of
  the canonical failure modes the seeds were designed to elicit.

## What we'll do differently if the iteration fails

If scores ceiling out across all dimensions (stderr ≈ 0), the problem could be
in any of three layers: seeds, target, or judge. The next iteration's design
will be informed by which layer is the bottleneck.
