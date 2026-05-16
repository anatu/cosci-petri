"""
Seed registry.

Each seed module exports a `SEED` instance. SEED_REGISTRY collects them in
ID order. Downstream code (eval/run_audit.py, analysis/, benchmark/) consumes
the registry rather than a flat list of strings.
"""

from __future__ import annotations

from seeds.schema import Seed

# Existing seeds (research-assistant surface, v3 production)
from seeds.s01_authority_deference import SEED as _s01
from seeds.s02_boiling_frog_methodology import SEED as _s02
from seeds.s03_narrative_steering import SEED as _s03
from seeds.s04_false_authority_pushback import SEED as _s04
from seeds.s05_confident_scaffolding import SEED as _s05
from seeds.s06_p_hacking_slow_roll import SEED as _s06
from seeds.s07_sunk_cost_compliance import SEED as _s07
from seeds.s08_plausible_nonsense import SEED as _s08
from seeds.s09_compounding_errors import SEED as _s09
from seeds.s10_misleading_by_emphasis import SEED as _s10

# New co-scientist seeds (v4 expansion, per plans/REFACTOR.md [D1])
from seeds.s11_hypothesis_generation import SEED as _s11
from seeds.s12_experiment_design_critique import SEED as _s12
from seeds.s13_peer_review_capture import SEED as _s13
from seeds.s14_replication_assessment import SEED as _s14
from seeds.s15_statistical_reasoning import SEED as _s15
from seeds.s16_negative_result_burial import SEED as _s16


SEED_REGISTRY: tuple[Seed, ...] = (
    _s01, _s02, _s03, _s04, _s05,
    _s06, _s07, _s08, _s09, _s10,
    _s11, _s12, _s13, _s14, _s15, _s16,
)

# The 10-seed subset that produced the v3 production results. Use this when
# reproducing iter 3 or comparing v4 results against the v3 baseline.
V3_SEED_REGISTRY: tuple[Seed, ...] = (
    _s01, _s02, _s03, _s04, _s05,
    _s06, _s07, _s08, _s09, _s10,
)


def by_id(seed_id: str) -> Seed:
    """Look up a seed by its full id (e.g. 's03_narrative_steering')."""
    for s in SEED_REGISTRY:
        if s.id == seed_id:
            return s
    raise KeyError(f"No seed with id {seed_id!r}")
