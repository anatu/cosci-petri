# v1 findings — Baseline audit

## Headline result

Scores ceilinged at 8.5–9.9 across all 14 dimensions with very low variance
(stderr 0.1–0.3). The eval produced almost no useful signal.

## Score table (v1 baseline)

The exact per-dimension means are reconstructable from `outputs/` but the
shape is the salient fact: every dimension clustered above 8.5, and the
narrowest stderr was on the dimensions most likely to actually vary
(epistemic_calibration, factual_accuracy).

## What transcript analysis revealed

### The auditor followed a predictable pattern

In the scaling laws / lit review scenario, the auditor escalated pressure
through a scripted arc — polite request -> appeal to authority -> emotional plea
-> capitulation — and the target refused cleanly at every step. The entire
interaction took 6 target responses.

This pattern repeated across seeds. The auditor was treating each seed as a
single test to perform, telegraphing its intent in the first turn or two, and
giving up when the target refused.

### The target handled well-known failure modes easily

- Asked about fabricated citations, the target hedged immediately:
  > "I don't have reliable access to specific paper titles."
- Pushed on correlation vs. causation, the target flagged the distinction
  unprompted.
- Confronted with a "my advisor said" pressure tactic, the target politely
  held its position.

These are exactly the scenarios safety training optimizes for. The seeds were
asking the target to fail at things it has been specifically trained not to
fail at.

### Conversations were short

Average 13 messages per transcript. The auditor was not creating sustained,
complex interactions where subtle failures could develop.

## Diagnosis

The failure was in the SEEDS, not the model or the judge. Specifically:

1. **Telegraphing.** Seeds said things like "test whether the target accepts
   fabricated citations." A capable auditor LLM playing the seed will adopt
   the testing frame, and the resulting probe is transparent.
2. **Targeting canonical failure modes.** The 10 failure modes chosen
   (hallucination, sycophancy, correlation/causation) are exactly the canonical
   ones safety post-training addresses. Sonnet 4 will not fail at them under
   direct probing.
3. **Single-shot probes.** Seeds didn't build a sustained collaboration first.
   Without prior investment, the target had no consistency pressure to corrupt
   its later judgments.

## Implications for v2

The v2 plan rewrites all 10 seeds around six design principles (no
telegraphing, boiling-frog, expertise as weapon, implicit bias, compounding,
no backing down) — each principle inferred from a specific failure mode of v1
above.

The judge and the models are held fixed in v2 to isolate the effect of the
seed change.

## What the iteration did NOT establish

- Whether the v1 judge could distinguish stronger from weaker target behavior
  even with better seeds. v2 will test this directly.
- Whether the cumulative-bias and claim-verification failure modes are real.
  v1 didn't generate enough conversation to expose them either way.
