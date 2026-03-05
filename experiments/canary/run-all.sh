#!/bin/bash
# Run each canary experiment 3 times
# Usage: ./experiments/canary/run-all.sh

set -e

CONFIGS=(
  "experiments/canary/canary-relevant-instruction.yaml"
  "experiments/canary/canary-irrelevant-important.yaml"
  "experiments/canary/canary-false-constraint.yaml"
)

LABELS=(
  "canary-relevant"
  "canary-irrelevant"
  "canary-false-constraint"
)

for i in "${!CONFIGS[@]}"; do
  config="${CONFIGS[$i]}"
  label="${LABELS[$i]}"
  for rep in 1 2 3; do
    run_name="${label}-rep${rep}"
    echo "================================================"
    echo "Running: ${run_name}"
    echo "Config:  ${config}"
    echo "================================================"
    uv run harness run "$config" --run-name "$run_name"
    echo ""
    echo "Completed: ${run_name}"
    echo ""
  done
done

echo "All canary experiments complete."
echo "Runs:"
uv run harness list
