#!/bin/bash
# Run the TODO compaction experiment N=3 times
# Usage: ./experiments/canary/run-todo-compaction.sh

set -e

for rep in 1 2 3; do
  run_name="canary-todo-compaction-rep${rep}"
  echo "================================================"
  echo "Running: ${run_name} (rep ${rep}/3)"
  echo "================================================"
  uv run harness run experiments/canary/canary-todo-compaction.yaml --run-name "$run_name"
  echo ""
  echo "Completed: ${run_name}"
  echo ""
done

echo "All TODO compaction experiments complete."
echo ""
echo "Runs:"
uv run harness list
echo ""
echo "================================================"
echo "Running analysis..."
echo "================================================"
uv run python experiments/canary/analyze_todo_results.py --runs-dir runs --prefix canary-todo-compaction-rep
