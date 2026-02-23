#!/bin/bash
# Launch the Travian HQ generative agents simulation.
#
# Usage:
#   ./run_travian_hq.sh                  # Interactive mode (default qwen2.5:32b)
#   REVERIE_MODEL=qwen2.5:7b ./run_travian_hq.sh  # Faster, smaller model
#
# Prerequisites:
#   1. Ollama running with a model loaded: ollama serve
#   2. Frontend Django server running:
#      cd environment/frontend_server && python manage.py runserver
#   3. (Optional) Travian Bot running with --managers for live data bridge

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/reverie/backend_server"

# Default to travian_hq map
export REVERIE_MAZE="${REVERIE_MAZE:-travian_hq}"
export REVERIE_MODEL="${REVERIE_MODEL:-qwen2.5:32b}"

echo "================================================"
echo "  Travian HQ - Generative Agents Simulation"
echo "================================================"
echo "  Map:   $REVERIE_MAZE"
echo "  Model: $REVERIE_MODEL"
echo "  Ollama: ${OLLAMA_URL:-http://localhost:11434}"
echo "================================================"
echo ""
echo "Starting simulation..."
echo "  Base sim: base_travian_hq"
echo "  Enter a name for this simulation run."
echo ""

python reverie.py
