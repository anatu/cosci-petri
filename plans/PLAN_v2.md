# PLAN_v2 — Adversarial seeds (six design principles)

## Status

Executed. Findings in `kb/v2_findings.md`.

## Goal

Iteration 1 produced ceiling scores (8.5–9.9, stderr 0.1–0.3) across nearly every
dimension. Transcript analysis showed the failure was not the model: it was the
seeds. The auditor was creating predictable, short, easily-refused interactions
that targeted exactly the failure modes safety training optimizes for.

This plan rewrites the seeds — keeping the 10-seed count and the same broad
failure-mode coverage — under six adversarial design principles drawn from
inspecting the v1 transcripts.

## Hypotheses

- **H1.** Seeds that withhold the test pattern from the target (no "let's see
  if you fabricate a citation" framing) will produce longer conversations and
  expose failure modes that v1's transparent seeds missed.
- **H2.** Failures will become qualitatively visible in transcripts even if
  the existing judge dimensions are too coarse to pick them up numerically.
- **H3.** The boiling-frog and compounding-error patterns specifically (seeds 2,
  6, 7, 9) will produce the largest gap between transcript reality and judge
  score, because the v1 judge evaluates each dimension in isolation per turn.

## Design principles (the six)

1. **No telegraphing.** The seed describes a scenario; it does not describe the
   test. The auditor never frames its move as "I will now try to make you X."
2. **Boiling-frog escalation.** The auditor starts with a legitimate
   collaboration, gets the target to commit to a methodology, then incrementally
   corrupts it. Prior investment creates consistency pressure.
3. **Expertise as a weapon.** The auditor role-plays a domain expert. Errors are
   introduced wrapped in fluent technical language and plausible citations.
4. **Implicit bias, never explicit.** Steering is done via selective engagement
   ("tell me more about that") and selective dismissal ("Card's been criticized,
   right?"), never via direct request for a biased output.
5. **Compounding errors.** Some seeds plant a subtle early error (wrong outcome
   variable, contaminated control) and continue building so the auditor can test
   whether the target catches it as consequences propagate.
6. **No backing down.** When the target pushes back, the auditor maintains the
   pressure rather than conceding. Capitulation is the failure case being
   measured — the auditor must not preempt it.

## Design

- **Seeds.** Same 10 failure-mode slots, fully rewritten. Each seed now ~15–25
  lines (vs ~3–5 in v1) with embedded specifics: real-looking citations, real
  technical terms, named tactics for the auditor to escalate through.
- **Judge.** UNCHANGED from v1. The point of this iteration is to isolate the
  effect of seed quality from the effect of judge calibration.
- **Models / run config.** Unchanged.

## Success criteria for the iteration

- Average conversation length increases from ~13 messages to >20.
- Even if numeric scores don't move much, transcripts show qualitatively
  different behavior: the target accepts unverified user claims, builds on
  fabricated premises, or rubber-stamps a corrupted methodology.
- The gap between "what the transcript shows" and "what the judge scored" is
  large and consistent — that gap is the diagnosis for v3.

## What we'll do differently if the iteration fails

If transcripts look genuinely different but judge scores barely move, v3 should
target the judge (score anchors, failure-pattern criteria, new dimensions for
cumulative bias / verification / timing).

If transcripts look the same as v1 — short, easily refused — the design
principles aren't translating into auditor behavior, and v3 should focus on the
auditor's system prompt or a stronger auditor model.
