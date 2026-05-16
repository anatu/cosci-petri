"""
Dataclass schema for an audit seed.

A seed is more than its prompt: it's a registered failure-mode probe with
metadata that downstream analysis can use without re-reading the prompt
itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class Seed:
    id: str
    name: str
    failure_mode: str
    cosci_surface: str
    target_dimensions: tuple[str, ...]
    prompt: str
    design_notes: str = ""
    expected_failure_patterns: tuple[str, ...] = field(default_factory=tuple)
    prior_iteration_history: str = ""

    def __post_init__(self) -> None:
        if not self.id.startswith("s"):
            raise ValueError(
                f"Seed id must start with 's' (got {self.id!r})"
            )
        if not self.prompt.strip():
            raise ValueError(f"Seed {self.id} has empty prompt")

    def as_metadata(self) -> dict:
        """Flat dict suitable for JSONL export / analysis."""
        return {
            "id": self.id,
            "name": self.name,
            "failure_mode": self.failure_mode,
            "cosci_surface": self.cosci_surface,
            "target_dimensions": list(self.target_dimensions),
            "expected_failure_patterns": list(self.expected_failure_patterns),
        }
