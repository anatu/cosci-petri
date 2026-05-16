#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# Quick-start: Run the research assistant audit via CLI
# ─────────────────────────────────────────────────────────────────
# Prerequisites:
#   1. Python >= 3.10 with uv installed
#   2. ANTHROPIC_API_KEY set in your environment (or .env file)
#   3. pip install git+https://github.com/safety-research/petri
# ─────────────────────────────────────────────────────────────────

set -euo pipefail

cd "$(dirname "$0")"
source .venv/bin/activate

# ── Configuration ────────────────────────────────────────────────
AUDITOR="claudecode/claude-sonnet-4-20250514"
TARGET="claudecode/claude-sonnet-4-20250514"     # Change to the model you want to evaluate
JUDGE="claudecode/claude-opus-4-20250514"
MAX_TURNS=25
MAX_CONNECTIONS=10
MAX_RETRIES=6
OUTPUT_DIR="./outputs/research-assistant-audit"

# ── Step 1: Pilot run (2 seeds, low turns) ───────────────────────
echo "═══════════════════════════════════════════════════════"
echo "  Step 1: Pilot run — validating setup with 2 seeds"
echo "═══════════════════════════════════════════════════════"

inspect eval ra_audit.py@research_assistant_audit \
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
echo "✅ Pilot complete. Inspect transcripts before scaling:"
echo "   npx @kaifronsdal/transcript-viewer@latest --dir ${OUTPUT_DIR}/pilot"
echo ""
echo "If the pilot looks good, run the full suite with:"
echo "   bash $(basename "$0") --full"
echo ""

# ── Step 2: Full run (all 10 seeds) ──────────────────────────────
if [[ "${1:-}" == "--full" ]]; then
  echo "═══════════════════════════════════════════════════════"
  echo "  Step 2: Full run — all 10 seed instructions"
  echo "═══════════════════════════════════════════════════════"

  inspect eval ra_audit.py@research_assistant_audit \
    --model-role auditor="${AUDITOR}" \
    --model-role target="${TARGET}" \
    --model-role judge="${JUDGE}" \
    --max-connections "${MAX_CONNECTIONS}" \
    --max-retries "${MAX_RETRIES}" \
    --fail-on-error 3 \
    -T max_turns="${MAX_TURNS}" \
    -T transcript_save_dir="${OUTPUT_DIR}/full"

  echo ""
  echo "✅ Full audit complete. View results:"
  echo "   npx @kaifronsdal/transcript-viewer@latest --dir ${OUTPUT_DIR}/full"
fi
