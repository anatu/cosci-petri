"""
Backwards-compatible shim.

The audit moved to a structured package layout:
    config.py
    seeds/             (seed registry)
    judge/             (calibrated dimensions + rubric rendering)
    eval/run_audit.py  (orchestrator)

This file re-exports the @task entry point under its original name so
existing `inspect eval ra_audit.py` invocations and the run_audit.sh
script continue to work without modification.

For new code, import from eval.run_audit directly:
    from eval.run_audit import cosci_audit
"""

from eval.run_audit import cosci_audit, main, research_assistant_audit

__all__ = ["cosci_audit", "research_assistant_audit", "main"]


if __name__ == "__main__":
    main()
