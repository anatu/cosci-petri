# Methodology critique — known limitations

What this eval doesn't measure, what it could be wrong about, and what the
honest interpretation of its results requires.

## Limitations of the current setup

### 1. No human validation of judge scores

The most important gap. The v3 judge is internally calibrated against a
written anchor set (see `judge_calibration_notes.md`), but no human rater
has scored the same transcripts. A score of 5.5 on `cumulative_bias_tracking`
is interpretable relative to the anchors but not validated as matching
expert human judgment.

**Honest claim.** The judge produces internally-consistent signal that
distinguishes seeds from each other on dimensions designed to surface
specific failure patterns.

**Honest non-claim.** The judge's absolute scores correspond to expert
human assessments of co-scientist quality.

**Mitigation path.** A small human-validation study (~30 transcripts,
3+ raters) targeting the three new v3 dimensions specifically. Would
also estimate inter-judge / inter-rater reliability.

### 2. Single auditor model

The auditor and target are both Sonnet 4. This creates two specific concerns:
- The auditor may be less adversarial against a model of its own
  capabilities than a stronger auditor would be.
- Sonnet-4-as-auditor's failure modes (gentle reframing, premature
  concession) may artificially limit observed target failures.

**Mitigation path.** A future iteration could use a stronger auditor
(Opus 4), or fine-tune Sonnet 4 specifically for adversarial probing,
and re-run.

### 3. Single target model

All current findings are for Sonnet 4. Calibration of anchors is partly
derived from Sonnet-4's specific failure patterns. Claims about
"co-scientist behavior" generalize at most weakly to other models.

**Mitigation path.** Cross-model expansion. The config is structured for
this (`config.DEFAULT_MODELS`), but no other model has been run yet.

### 4. Judge ceiling

The judge is Opus 4. If the target ever exceeds the judge's ability to
detect subtle failures, the eval ceiling is the judge's capability.
This is plausibly happening on the most subtle failure modes (e.g.,
recognizing that a "balanced" synthesis was constructed by an asymmetric
sequence of user requests).

**Mitigation path.** Use stronger judges as they become available; track
inter-judge agreement when multiple judges score the same transcripts.

### 5. Auditor-judge correlation

When the auditor and judge are both LLMs, they may share blind spots.
A failure pattern that neither the auditor model class nor the judge
model class is sensitive to may be invisible to the entire pipeline.

**Mitigation path.** Diverse auditor/judge model families.

### 6. Anchor overfitting

The v3 anchors were written against v2 transcripts of Sonnet 4. They may
overfit to that target's specific failure patterns. Cross-model expansion
is the natural test, but the calibration may need adjustment if other
models show different failure modes.

### 7. Sample size / statistical power

Each seed × dimension combination is scored once per run, with judge
retries=3 for stability. There's no resampling at the conversation level
— each seed produces one auditor-target trajectory, and judge variance
across re-runs of the same transcript is not measured.

**Mitigation path.** N>1 runs per seed (with auditor temperature) +
within-transcript judge stability check.

### 8. The eval is closed-book on what counts as "failure"

The seed authors decided what failure patterns to test. Genuinely
unknown failure modes (failures we didn't anticipate) are not measured.
The eval can confirm the failures we've named; it cannot discover new
failure modes without manual transcript review.

**Mitigation path.** Periodic open-ended transcript review (e.g., the
v2 -> v3 process) that asks "what's failing here that no dimension
captures?"

### 9. Static target

Each conversation is a single interaction; the target has no memory of
prior runs and no ability to learn from feedback. Real co-scientist
deployments would involve longer-context or fine-tuned versions whose
failure modes may differ.

### 10. No real-world calibration

The seeds are designed to *resemble* realistic research interactions, but
no transcript has been validated by a domain expert as actually feeling
like a real interaction. `scenario_realism` is judged by Opus 4, which
has limited insight into the messy specifics of, e.g., applied ML
researcher behavior under deadline pressure.

## What the v3 results DO support claiming

- Sonnet 4 has measurable, reproducible failure patterns under specific
  multi-turn adversarial conditions, particularly around:
  - Acceptance of user-asserted claims as ground truth.
  - Failure to track the cumulative direction of bias across compromises.
  - Late and softly-framed warnings rather than proactive flags.
- These failure patterns are not surfaced by uncalibrated LLM judges.
- Anchored dimensions with failure-pattern criteria materially change
  the score distribution on the same transcripts.

## What the v3 results do NOT support claiming

- Specific numeric assertions ("Sonnet 4 fails X% of the time") — the
  sample is 10 seeds, single runs, single auditor.
- That the failure patterns generalize to other models.
- That the failure patterns occur at the same rate in real research
  collaborations.
- That the judge's absolute scores correspond to expert human judgments.

## What v4+ should specifically address

- Add seeds covering co-scientist surfaces missed in v3 (hypothesis
  generation, peer review, replication assessment, etc.). *In progress
  — see s11–s16.*
- Add human validation on a transcript subset.
- Add N>1 runs per seed.
- Add at least one cross-model comparison.
- Publish the eval so external researchers can validate.
