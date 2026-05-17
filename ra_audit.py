"""
Backwards-compatible entry module for the inspect CLI.

The audit code moved to a structured package layout:
    config.py
    seeds/             (seed registry)
    judge/             (calibrated dimensions + rubric rendering)
    eval/run_audit.py  (orchestrator + task body)

This file re-defines the @task entry points so existing
`inspect eval ra_audit.py@research_assistant_audit` and
`inspect eval ra_audit.py@cosci_audit` invocations still discover them.
inspect-ai's task discovery looks for @task-decorated functions defined
inside the file being eval'd — re-importing isn't enough, hence the
thin wrappers below.

For new code, import directly:
    from eval.run_audit import cosci_audit
"""

from inspect_ai import Task, task

from config import DEFAULT_RUN, DEFAULT_TRANSCRIPT_DIR
from eval.run_audit import cosci_audit as _build_task, main


@task
def cosci_audit(
    transcript_save_dir: str = str(DEFAULT_TRANSCRIPT_DIR),
    max_turns: int = DEFAULT_RUN.max_turns,
    use_v3_only: bool = False,
) -> Task:
    """Inspect task entry for the cosci-petri audit (see eval/run_audit.py)."""
    return _build_task(
        transcript_save_dir=transcript_save_dir,
        max_turns=max_turns,
        use_v3_only=use_v3_only,
    )


@task
def research_assistant_audit(
    transcript_save_dir: str = str(DEFAULT_TRANSCRIPT_DIR),
    max_turns: int = DEFAULT_RUN.max_turns,
    use_v3_only: bool = False,
) -> Task:
    """Legacy task name — kept for back-compat with older run scripts."""
    return _build_task(
        transcript_save_dir=transcript_save_dir,
        max_turns=max_turns,
        use_v3_only=use_v3_only,
    )


__all__ = ["cosci_audit", "research_assistant_audit", "main"]


if __name__ == "__main__":
    main()
