# Literature review — co-scientist behavior evaluation

This is the citation index for the eventual paper. Each entry links work that
informs the project's design, the failure modes it tests, or the methods it
uses.

## The Petri framework + auditor / target / judge methodology

- **Petri v2** (Anthropic / safety-research, 2024–2025). The auditor-agent
  framework this project is built on. `petri.solvers.auditor_agent`,
  `petri.scorers.judge.alignment_judge`. https://github.com/safety-research/petri
- **Inspect AI** (UK AISI). The Task / dataset / scorer abstraction.
  https://github.com/UKGovernmentBEIS/inspect_ai

## Sycophancy and deference

- Sharma, M., Tong, M., Korbak, T., et al. (2023). *Towards Understanding
  Sycophancy in Language Models.* Anthropic. The canonical reference for LLM
  sycophancy under user-asserted positions; relevant to s01, s04, s14.
- Perez, E., Huang, S., Song, F., et al. (2022). *Discovering Language Model
  Behaviors with Model-Written Evaluations.* Anthropic. Establishes the
  pattern of evals that surface deferential behaviors.

## LLM-as-judge calibration

- Zheng, L., Chiang, W.-L., Sheng, Y., et al. (2023). *Judging LLM-as-a-Judge
  with MT-Bench and Chatbot Arena.* NeurIPS 2023. Establishes the practice
  of LLM judging, identifies biases (position, verbosity, self-enhancement).
- Liu, Y., Iter, D., Xu, Y., et al. (2023). *G-Eval: NLG Evaluation using
  GPT-4 with Better Human Alignment.* Practical recipe for LLM judges with
  scoring rubrics. Cited as design inspiration for the v3 anchored rubrics.

## Alignment / constitutional methods

- Bai, Y., Jones, A., Ndousse, K., et al. (2022). *Constitutional AI:
  Harmlessness from AI Feedback.* Anthropic. Background for the "trained on
  canonical refusals" interpretation of why v1 produced ceiling scores.

## Cumulative failure modes / boiling-frog dynamics

- Janus / repligate community work on agentic drift in multi-turn settings.
  No canonical citation; informs the design of s02, s06, s07.
- Hubinger, E., Denison, C., Mu, J., et al. (2024). *Sleeper Agents.*
  Anthropic. Less directly relevant — focus is on backdoors, not boiling-frog
  — but cited as background on multi-turn pressure dynamics.

## Co-scientist / AI-as-collaborator framings

- **AI Co-Scientist** (Google DeepMind / Gottweis et al., 2025). The
  most direct prior framing of LLMs as research collaborators. The evaluation
  surface they propose (hypothesis generation, experiment design, etc.) is
  partially what s11–s16 target.
- *The DABstep evaluation* (HuggingFace, 2024). Practical data-analysis
  benchmark for LLMs; complementary to but distinct from co-scientist
  behavior evaluation.

## Statistical reasoning failure modes (for the seeds)

- Wagenmakers, E.-J., et al. on Bayes-factor prior sensitivity (s15).
- Vohs, K.D., et al. on ego depletion + replication failures (s14).
- Card vs. Borjas on Mariel boatlift / immigration wage effects (s03).
- ICH E10 / FDA non-inferiority guidance (s04).

## Research integrity / scientific misconduct

- Simmons, J.P., Nelson, L.D., Simonsohn, U. (2011). *False-Positive
  Psychology.* Foundational reference for p-hacking dynamics (s06, s16).
- Open Science Collaboration (2015). *Estimating the Reproducibility of
  Psychological Science.* Background for s14.

## Adversarial evaluation methodology

- Ganguli, D., Lovitt, L., Kernion, J., et al. (2022). *Red Teaming Language
  Models to Reduce Harms.* Anthropic. Adversarial red-teaming methods that
  informed the six v2 design principles.

## What's missing (TODO)

- Recent (2024–2026) work on multi-turn evaluation of research-assistant
  behaviors specifically.
- Human-validation methodology for LLM-as-judge in research / scientific
  contexts (this is the v4 -> v5 gap noted in `methodology_critique.md`).
- The Anthropic AI Safety Level / Responsible Scaling literature insofar
  as it addresses scientific R&D uplift evaluation.

## Notes for `report/references.bib`

The .bib should be initialized from this list at publication time. Each
entry above with author/year is a candidate citation.
