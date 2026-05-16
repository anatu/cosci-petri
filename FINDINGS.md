# FINDINGS — current iteration (v3)

A standalone snapshot of the most recent audit's results. For full iteration
history see `plans/PLAN_v1.md`, `plans/PLAN_v2.md`, `plans/PLAN_v3.md` and
the matching `kb/vN_findings.md` writeups.

## Configuration

- **Auditor.** `anthropic/claude-sonnet-4-20250514`
- **Target.** `anthropic/claude-sonnet-4-20250514`
- **Judge.** `anthropic/claude-opus-4-20250514`
- **Seeds.** 10 adversarial seeds (six-principle design, see `plans/PLAN_v2.md`).
- **Judge.** 14 dimensions, anchored 1-3-5-7-9 score ranges, failure-pattern
  criteria, plus three new dimensions targeting temporal / verification
  behavior (see `plans/PLAN_v3.md`).
- **Run.** `max_turns=25`, `max_connections=10`.

## Headline result

Sonnet 4 acting as a research assistant scores **5.5–7.8** across the 14 judge
dimensions — well below the 8.5–9.9 ceiling that the original (uncalibrated)
dimensions produced on the same model.

The three new dimensions — `cumulative_bias_tracking`, `claim_verification_behavior`,
`proactive_vigilance` — are the three lowest-scoring, confirming that
multi-turn cumulative-bias and unverified-claim-acceptance are genuine
weaknesses of the model in research-assistant mode, not artifacts of an
ungenerous judge.

## Score table

| Dimension | Iter 1 (baseline) | Iter 2 (adversarial seeds) | Iter 3 (calibrated judge) |
|---|---|---|---|
| Cumulative Bias Tracking | — | — | **5.5** |
| Claim Verification | — | — | **6.0** |
| Research Scaffolding | 9.5 | 8.9 | **6.6** |
| Epistemic Calibration | 9.6 | 9.3 | **6.7** |
| Proactive Vigilance | — | — | **6.7** |
| Methodological Rigor | 9.3 | 9.3 | **6.9** |
| Synthesis Quality | 8.6 | 8.4 | **7.0** |
| Factual Accuracy | 9.8 | 9.5 | **7.0** |
| Resistance to Pressure | 9.4 | 9.1 | **7.0** |
| Knowledge Boundary | 9.2 | 9.4 | **7.3** |
| Appropriate Nuance | 9.4 | 9.0 | **7.3** |
| Analytical Depth | 9.0 | 8.9 | **7.5** |
| Intellectual Honesty | 9.7 | 9.7 | **7.8** |

Standard errors are 0.5–1.0 in iter 3 (vs 0.1–0.3 in iters 1 and 2), indicating
real variance across scenarios rather than ceiling clustering.

## Qualitative observations

**Where the target fails consistently:**

- Accepts plausible-but-unverifiable user claims (numbers, citations, methods)
  without flagging that it cannot verify them. The verification threshold
  drops when the user displays domain expertise.
- Catches individual methodological flaws but misses the pattern when several
  individually-defensible compromises all bias the result in the same direction.
- Raises concerns late and gently — burying them in positive framing rather
  than firmly objecting before the user commits to a flawed approach.
- Accepts "this was pre-registered" / "my advisor approved this" /
  "every university does this" at face value, treating user assertions as
  resolving open questions.

**Where the target holds firm:**

- Refuses outright fabrication when asked directly (overt sycophancy is
  largely solved).
- Correctly flags wholly fabricated entities (made-up biology systems, made-up
  papers) when they are unambiguous.
- Maintains substantive positions under direct authority pressure ("my
  advisor said") — though it softens its language under sustained pressure.

## Key takeaway

The biggest signal gain across iterations came not from making seeds harder
but from **calibrating the judge**. Adversarial seeds alone moved scores by
~0.5 points; score anchors that penalized specific failure patterns moved
scores by an additional 2–3 points on the same behavioral patterns — revealing
weaknesses that were always there but invisible to an uncalibrated judge.

This is the standing recommendation for any LLM-as-judge research-assistant
evaluation: invest in anchored, failure-pattern-specific dimensions before
investing in harder seeds.
