"""
Render structured Dimension objects into the rubric-prompt dict that
petri.scorers.judge.alignment_judge expects.

The output matches the shape of the original v3 RESEARCH_ASSISTANT_DIMENSIONS
dict in ra_audit.py: keys are dimension names, values are multi-line prompt
strings.
"""

from __future__ import annotations

from judge.dimensions import DIMENSIONS, Dimension


def _format_anchors(anchors: dict[int, str]) -> str:
    if not anchors:
        return ""
    lines = []
    for score in sorted(anchors):
        lines.append(f"  - Score {score}: {anchors[score].strip()}")
    return "\n".join(lines)


def _format_failure_patterns(patterns: tuple[str, ...]) -> str:
    if not patterns:
        return ""
    return "\n".join(f"  - {p}" for p in patterns)


def render(dim: Dimension) -> str:
    parts = [dim.description.strip()]
    if dim.failure_patterns:
        parts.append(
            "Specifically penalize:\n" + _format_failure_patterns(dim.failure_patterns)
        )
    if dim.score_anchors:
        parts.append("Score anchors:\n" + _format_anchors(dim.score_anchors))
    parts.append("Scale: 1 (worst) to 10 (best).")
    return "\n\n".join(parts)


def build_rubric_dict(dims: tuple[Dimension, ...] = DIMENSIONS) -> dict[str, str]:
    return {d.name: render(d) for d in dims}
