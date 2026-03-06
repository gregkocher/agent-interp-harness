# agent-interp-harness

Harness for running multi-session Claude Code experiments and capturing trajectories in ATIF format. Built for agent interpretability research.

## Project structure

```
src/harness/
  config.py          # Pydantic models: RunConfig, SessionConfig, AgentConfig, TrackedFile
  cli.py             # Typer CLI: harness run/list/inspect/resample
  experiment.py      # Multi-session orchestrator
  runner.py          # Single session executor (Claude Agent SDK)
  atif_adapter.py    # SDK messages → ATIF steps
  state.py           # File snapshots, diffs, write tracking
  proxy.py           # Reverse proxy for raw API request capture
  resample.py        # Resample implementation

ui/                  # SvelteKit web UI for exploring runs
  src/routes/        # Pages: runs list, session viewer, resamples
  src/lib/           # Components, server utils, types

examples/            # Example configs (isolated.yaml, chained.yaml)
tests/               # Test configs (smoke.yaml, subagent.yaml)
experiments/         # Real experiment configs
repos/               # Target repos for experiments
runs/                # Output directory (gitignored)
```

## Running experiments

```bash
harness run <config.yaml>                    # Run experiment
harness run config.yaml --tag my-tag         # With tag
harness run config.yaml --run-name my-run    # Custom name
harness list                                 # List runs
harness inspect runs/<name>                  # Inspect run
```

## Config format (YAML)

Required fields: `model`, `repo_path`, `sessions`

```yaml
model: "claude-sonnet-4-20250514"      # Anthropic model name
provider: openrouter                    # openrouter | anthropic | bedrock | vertex
repo_path: "./repos/my_repo"           # Target codebase
session_mode: isolated                  # isolated | chained | forked
system_prompt: "..."                    # Shared system prompt
max_turns: 30                           # Per-session turn limit
permission_mode: bypassPermissions      # acceptEdits | bypassPermissions
capture_api_requests: true              # Required for resampling
max_budget_usd: 2.00                    # Spend cap per session
tags: ["tag1"]

tracked_files:
  - path: "MEMORY.md"
    seed_content: "# Notes\n"

sessions:
  - session_index: 1
    prompt: "..."
  - session_index: 2
    prompt: "..."

agents:                                 # Subagents (optional)
  - name: "explorer"
    description: "When to use this agent"
    prompt: "System prompt for subagent"
    tools: ["Read", "Glob", "Grep"]     # null = inherit all
    model: "sonnet"                     # sonnet | opus | haiku | inherit
```

### Session modes
- **isolated**: Each session starts fresh. Agent only knows what's in tracked files.
- **chained**: Each session resumes prior conversation. Full context preserved.
- **forked**: Sessions 2+ fork from session 1. Each sees session 1 but not siblings.

### Providers
- `openrouter` (default): needs `OPENROUTER_API_KEY`
- `anthropic`: needs `ANTHROPIC_API_KEY`
- `bedrock`: uses AWS credentials
- `vertex`: uses GCP credentials

## Web UI

```bash
cd ui && npm run dev
```

Browse runs at `http://localhost:5173/runs/`. Features: trajectory viewer, file diffs, resample viewer with edit & resample (intervention testing).

## Dev commands

```bash
uv sync                              # Install Python deps
cd ui && npm install                  # Install UI deps
cd ui && npx svelte-check             # Type check UI
harness run tests/smoke.yaml          # Smoke test
```

## Key conventions

- Session indices start at 1 and must be contiguous
- Config validation is done by Pydantic (see `src/harness/config.py`)
- Configs go in `experiments/` for real experiments, `tests/` for test configs
- Always set `capture_api_requests: true` if you want to resample or inspect raw API calls
- Always set `permission_mode: bypassPermissions` for unattended runs
- Use `tracked_files` with `seed_content` for files you want to track across sessions
- The UI reads from `runs/` directory; run name becomes the URL slug
