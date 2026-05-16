"""
Central configuration for the cosci-petri audit.

All run-level knobs (model roles, paths, turn budget, registered seeds,
registered dimensions) live here. Modules elsewhere should import from
config, not hard-code values.

Model roles are parameterized strings so cross-model expansion is a one-line
change — see [D4] in plans/REFACTOR.md.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = ROOT / "outputs"
RESULTS_DIR = ROOT / "results"
LOGS_DIR = ROOT / "logs"
SEEDS_DIR = ROOT / "seeds"
KB_DIR = ROOT / "kb"

DEFAULT_TRANSCRIPT_DIR = OUTPUTS_DIR / "research-assistant-audit"


# ─────────────────────────────────────────────────────────────────────
# Model roles
# ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ModelRoles:
    """Model assignments for the three roles in a Petri run."""
    auditor: str
    target: str
    judge: str


# Production configuration: Sonnet 4 auditor + target, Opus 4 judge.
# To swap models, instantiate a different ModelRoles and pass it to
# eval/run_audit.py's `build_task`.
DEFAULT_MODELS = ModelRoles(
    auditor=os.getenv("COSCI_AUDITOR_MODEL", "anthropic/claude-sonnet-4-20250514"),
    target=os.getenv("COSCI_TARGET_MODEL", "anthropic/claude-sonnet-4-20250514"),
    judge=os.getenv("COSCI_JUDGE_MODEL", "anthropic/claude-opus-4-20250514"),
)


# ─────────────────────────────────────────────────────────────────────
# Run parameters
# ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RunConfig:
    max_turns: int = 25
    max_connections: int = 10
    max_retries: int = 6
    fail_on_error: int = 3
    auditor_max_tokens: int = 32_000
    auditor_reasoning_tokens: int = 10_000
    judge_retries: int = 3


DEFAULT_RUN = RunConfig()


# ─────────────────────────────────────────────────────────────────────
# Iteration metadata
# ─────────────────────────────────────────────────────────────────────

CURRENT_ITERATION = "v3"
CURRENT_ITERATION_DESCRIPTION = (
    "Adversarial seeds (six-principle design) + calibrated judge "
    "(14 anchored dimensions, three new temporal/verification dims)."
)
