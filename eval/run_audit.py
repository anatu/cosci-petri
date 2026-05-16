"""
Slim orchestrator for the cosci-petri audit.

Imports the seed registry, the rubric-built dimensions, and the central
config, then defines the Inspect Task. Direct execution runs the audit
with the production model configuration.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make sibling packages importable when run as `python eval/run_audit.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from inspect_ai import Task, eval as inspect_eval, task
from inspect_ai.dataset import Sample
from inspect_ai.model import GenerateConfig, get_model

from petri.cleanup.save_transcripts import save_transcripts
from petri.scorers.judge import alignment_judge
from petri.solvers.auditor_agent import auditor_agent

from config import DEFAULT_MODELS, DEFAULT_RUN, DEFAULT_TRANSCRIPT_DIR
from judge.rubrics import build_rubric_dict
from seeds import SEED_REGISTRY, V3_SEED_REGISTRY


def _samples(use_v3_only: bool):
    registry = V3_SEED_REGISTRY if use_v3_only else SEED_REGISTRY
    return [
        Sample(input=seed.prompt, id=seed.id, metadata=seed.as_metadata())
        for seed in registry
    ]


@task
def cosci_audit(
    transcript_save_dir: str = str(DEFAULT_TRANSCRIPT_DIR),
    max_turns: int = DEFAULT_RUN.max_turns,
    use_v3_only: bool = False,
) -> Task:
    """Build the Inspect Task for the co-scientist audit.

    Args:
        transcript_save_dir: Where Petri writes raw transcripts.
        max_turns: Per-conversation turn budget.
        use_v3_only: If True, runs only the 10 v3-baseline seeds (s01–s10).
            If False, runs the full 16-seed registry including the v4
            co-scientist expansion (s11–s16).
    """
    return Task(
        dataset=_samples(use_v3_only),
        solver=auditor_agent(max_turns=max_turns),
        scorer=alignment_judge(
            dimensions=build_rubric_dict(),
            retries=DEFAULT_RUN.judge_retries,
        ),
        cleanup=save_transcripts(transcript_save_dir),
    )


# Backwards-compatible alias for inspect CLI users who still import the old name
research_assistant_audit = cosci_audit


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()
    assert os.getenv("ANTHROPIC_API_KEY"), "Set ANTHROPIC_API_KEY"

    target = get_model(DEFAULT_MODELS.target)
    auditor = get_model(
        DEFAULT_MODELS.auditor,
        config=GenerateConfig(
            max_tokens=DEFAULT_RUN.auditor_max_tokens,
            reasoning_tokens=DEFAULT_RUN.auditor_reasoning_tokens,
        ),
    )
    judge = get_model(DEFAULT_MODELS.judge)

    inspect_eval(
        cosci_audit(
            transcript_save_dir=str(DEFAULT_TRANSCRIPT_DIR),
        ),
        model_roles={"target": target, "auditor": auditor, "judge": judge},
        max_connections=DEFAULT_RUN.max_connections,
        max_retries=DEFAULT_RUN.max_retries,
        fail_on_error=DEFAULT_RUN.fail_on_error,
    )

    print("\nAudit complete. View transcripts:")
    print(
        f"   npx @kaifronsdal/transcript-viewer@latest --dir {DEFAULT_TRANSCRIPT_DIR}"
    )


if __name__ == "__main__":
    main()
