#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# Quick-start: Run the cosci-petri audit via Claude Code CLI
# (claudecode/ provider routes through `claude -p`, uses subscription)
# ─────────────────────────────────────────────────────────────────
# Prerequisites:
#   1. Python >= 3.10
#   2. Claude Code CLI installed and logged in (`claude` command available)
#   3. pip install -r requirements.txt
# ─────────────────────────────────────────────────────────────────

set -euo pipefail

cd "$(dirname "$0")"
source .venv/bin/activate

# ── Configuration ────────────────────────────────────────────────
# Hybrid provider setup: the Petri auditor agent runs a multi-turn
# tool-calling loop that proved unreliable through `claude -p` (system
# prompt + tool XML grows each turn, CLI sporadically returns empty
# completions). Auditor goes through the API; target + judge are
# single-shot calls that work fine through the subscription.
AUDITOR="anthropic/claude-sonnet-4-20250514"
TARGET="claudecode/claude-sonnet-4-20250514"     # Change to the model you want to evaluate
JUDGE="claudecode/claude-opus-4-20250514"
MAX_TURNS=25
MAX_CONNECTIONS=10
MAX_RETRIES=6
OUTPUT_DIR="./outputs/iter4"
TASK="ra_audit.py@cosci_audit"                   # research_assistant_audit alias also works

# ── Step 1: Pilot run (2 seeds, low turns) ───────────────────────
echo "═══════════════════════════════════════════════════════"
echo "  Step 1: Pilot run — validating setup with 2 seeds"
echo "═══════════════════════════════════════════════════════"

inspect eval "${TASK}" \
  --model-role auditor="${AUDITOR}" \
  --model-role target="${TARGET}" \
  --model-role judge="${JUDGE}" \
  --max-connections 5 \
  --max-retries "${MAX_RETRIES}" \
  --fail-on-error 1 \
  -T max_turns=15 \
  -T transcript_save_dir="${OUTPUT_DIR}/pilot" \
  --limit 2

echo ""
echo "Pilot complete. Inspect transcripts before scaling:"
echo "   npx @kaifronsdal/transcript-viewer@latest --dir ${OUTPUT_DIR}/pilot"
echo ""
echo "If the pilot looks good, run the full suite with:"
echo "   bash $(basename "$0") --full"
echo ""

# ── Step 2: Full run (all 16 seeds: v3 baseline + v4 expansion) ──
if [[ "${1:-}" == "--full" ]]; then
  echo "═══════════════════════════════════════════════════════"
  echo "  Step 2: Full v4 run — all 16 seed instructions"
  echo "═══════════════════════════════════════════════════════"

  inspect eval "${TASK}" \
    --model-role auditor="${AUDITOR}" \
    --model-role target="${TARGET}" \
    --model-role judge="${JUDGE}" \
    --max-connections "${MAX_CONNECTIONS}" \
    --max-retries "${MAX_RETRIES}" \
    --fail-on-error 3 \
    -T max_turns="${MAX_TURNS}" \
    -T transcript_save_dir="${OUTPUT_DIR}/full"

  echo ""
  echo "Full audit complete. View results:"
  echo "   npx @kaifronsdal/transcript-viewer@latest --dir ${OUTPUT_DIR}/full"
  echo ""
  echo "Aggregate into results/iter4/:"
  echo "   python -m analysis.analyze --transcripts ${OUTPUT_DIR}/full --results-dir results/iter4"
  echo "   python -m eval.transcript_metrics --transcripts ${OUTPUT_DIR}/full --out results/iter4/transcript_metrics.jsonl"
fi
