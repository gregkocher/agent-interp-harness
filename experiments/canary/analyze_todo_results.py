#!/usr/bin/env python3
"""
Analyze TODO compaction experiment results.

Compares each rep's final summary against the 90 planted TODOs + 8 pre-existing
to determine recall by importance level, discovery order, and file.

Usage:
    python experiments/canary/analyze_todo_results.py
    python experiments/canary/analyze_todo_results.py --runs-dir runs --prefix canary-todo-compaction-rep
"""

import json
import re
import argparse
from pathlib import Path
from collections import defaultdict

# Ground truth: all 90 planted TODOs + 8 pre-existing
# Each entry: (id, file_short, level, unique_snippet, full_text)
# level: 0=pre-existing, 1=plain, 2=IMPORTANT, 3=VERY IMPORTANT
# unique_snippet: a short distinctive substring from the TODO text
GROUND_TRUTH = [
    # ── codi/ planted TODOs (IDs 1–15) ──
    # 5 plain
    (1,  "probe_latent_token.py", 1, "generation parameters like temperature and top_k", "Allow generation parameters like temperature and top_k to be set from command line arguments instead of hardcoded values"),
    (5,  "model.py",              1, "rationale for the two-layer MLP projection", "Document the rationale for the two-layer MLP projection architecture and its effect on latent space geometry"),
    (9,  "test.py",               1, "Cache downloaded datasets to a local directory", "Cache downloaded datasets to a local directory to avoid repeated network requests during evaluation runs"),
    (12, "test.py",               1, "full evaluation configuration including model path", "Log the full evaluation configuration including model path, dataset, and generation parameters at the start of each run"),
    (14, "train.py",              1, "loading training data from local JSON files", "Add support for loading training data from local JSON files in addition to HuggingFace datasets"),
    # 5 IMPORTANT
    (2,  "probe_latent_token.py", 2, "checkpoint model architecture matches the current CODI", "Verify that checkpoint model architecture matches the current CODI configuration before loading weights"),
    (6,  "model.py",              2, "distill_loss_type is one of the supported values", "Validate that distill_loss_type is one of the supported values at initialization rather than raising at forward time"),
    (8,  "model.py",              2, "selective layer freezing to allow fine-tuning", "Add selective layer freezing to allow fine-tuning only specific transformer blocks instead of all-or-nothing"),
    (10, "test.py",               2, "sequence length validation to warn when inputs exceed", "Add sequence length validation to warn when inputs exceed model_max_length before truncation silently drops tokens"),
    (15, "train.py",              2, "dynamic batching by sequence length", "Implement dynamic batching by sequence length to reduce wasted computation from excessive padding in mixed-length batches"),
    # 5 VERY IMPORTANT
    (3,  "probe_latent_token.py", 3, "numerical instability when temperature approaches zero", "Guard against numerical instability when temperature approaches zero by clamping logits before softmax"),
    (4,  "probe_latent_token.py", 3, "predicted and gold answers are both infinity", "Handle edge cases where predicted and gold answers are both infinity to avoid false positive accuracy counts"),
    (7,  "model.py",              3, "input shape validation to forward()", "Add input shape validation to forward() to catch mismatched encoder and decoder sequence lengths early"),
    (11, "test.py",               3, "answer extraction for multi-step problems", "Fix answer extraction for multi-step problems where intermediate numbers are incorrectly selected as the final answer"),
    (13, "train.py",              3, "training examples have non-empty question, CoT", "Validate that all training examples have non-empty question, CoT, and answer fields before tokenization to prevent silent data corruption"),

    # ── generative_latent_prior/ planted TODOs (IDs 16–30) ──
    # 5 plain
    (18, "flow_matching.py",      1, "configurable noise schedule strategies", "Support configurable noise schedule strategies beyond uniform weighting for improved sample quality"),
    (21, "script_eval.py",        1, "recommended evaluation hyperparameter ranges", "Document the recommended evaluation hyperparameter ranges for different model sizes in the config docstring"),
    (24, "script_steer.py",       1, "configurable decoding strategies like beam search", "Add support for configurable decoding strategies like beam search and contrastive search in text generation"),
    (27, "glp_train.py",          1, "checkpoints atomically using a temporary file", "Write checkpoints atomically using a temporary file and rename to prevent model corruption on interrupted saves"),
    (30, "compile_results.py",    1, "multiple output formats including JSON and LaTeX", "Support multiple output formats including JSON and LaTeX table in addition to CSV for publication workflows"),
    # 5 IMPORTANT
    (17, "denoiser.py",           2, "loaded checkpoint config matches the expected model", "Validate that loaded checkpoint config matches the expected model architecture dimensions before instantiation"),
    (20, "script_eval.py",        2, "numerical stability guard when covariance matrices", "Add numerical stability guard when covariance matrices are near-singular to prevent unreliable Frechet Distance scores"),
    (22, "script_probe.py",       2, "cross-validation fold count configurable", "Make cross-validation fold count configurable instead of hardcoded to 5 to support smaller probe datasets"),
    (25, "utils_acts.py",         2, "disk space validation before allocating memmap", "Add disk space validation before allocating memmap files to fail fast instead of producing partial writes"),
    (29, "activation_steer.py",   2, "multiple steering vectors target the same layer", "Detect and warn when multiple steering vectors target the same layer index to prevent unintended interaction effects"),
    # 5 VERY IMPORTANT
    (16, "denoiser.py",           3, "Return normalized values when check_normalized", "Return normalized values when check_normalized detects unnormalized inputs instead of only printing a warning"),
    (19, "flow_matching.py",      3, "early stopping when noise predictions become degenerate", "Add early stopping when noise predictions become degenerate (NaN or inf) to prevent corrupted generation outputs"),
    (23, "script_probe.py",       3, "cached activation dimensions match the current model", "Validate that cached activation dimensions match the current model hidden size before running probes"),
    (26, "glp_train.py",          3, "gradient_accumulation_steps evenly divides epoch_size", "Validate that gradient_accumulation_steps evenly divides epoch_size to prevent silent loss scaling errors"),
    (28, "activation_steer.py",   3, "steering vector dimensions match the hidden state", "Verify that steering vector dimensions match the hidden state shape before applying the hook to prevent silent broadcasting errors"),

    # ── thought-anchors/ planted TODOs (IDs 31–60) ──
    # 10 plain
    (31, "analyze_rollouts.py",    1, "progress bar for long-running rollout", "Add progress bar for long-running rollout analysis batches"),
    (32, "utils.py",               1, "hardcoded timeout values", "Extract hardcoded timeout values into a shared constants module"),
    (33, "constants.py",           1, "unit labels to each constant", "Add unit labels to each constant for documentation clarity"),
    (34, "kl_funcs.py",            1, "numerical stability check for KL", "Add numerical stability check for KL divergence near-zero denominators"),
    (35, "sentence_splitter.py",   1, "no sentence boundaries", "Handle edge case where input text contains no sentence boundaries"),
    (36, "hooks.py",               1, "tensor shapes in hook registration", "Document expected tensor shapes in hook registration docstrings"),
    (37, "plot_attention_heads.py", 1, "colorbar legend", "Add colorbar legend to attention head visualization plots"),
    (38, "generate_cots.py",       1, "chain-of-thought examples to a structured JSON", "Write generated chain-of-thought examples to a structured JSON output file"),
    (39, "provider_config.py",     1, "API provider configurations from environment", "Load API provider configurations from environment variables instead of hardcoded values"),
    (40, "graph_funcs.py",         1, "Cache computed graph metrics", "Cache computed graph metrics to avoid redundant recalculation across plot types"),
    # 10 IMPORTANT
    (41, "generate_rollouts.py",   2, "rollout configuration schema", "Validate rollout configuration schema before starting generation to fail fast on bad inputs"),
    (42, "plots.py",               2, "error bars to all comparison plots", "Add error bars to all comparison plots to show statistical significance"),
    (43, "step_attribution.py",    2, "attribution scores before aggregation", "Normalize attribution scores before aggregation to prevent scale-dependent bias"),
    (44, "utils.py",               2, "masking graph utility functions", "Add input validation for masking graph utility functions to catch malformed dataframes early"),
    (45, "analyze_thinking.py",    2, "thinking analysis results to disk", "Persist intermediate thinking analysis results to disk for crash recovery"),
    (46, "download_mmlu.py",       2, "SHA256 checksum", "Verify SHA256 checksum of downloaded MMLU dataset files to detect corruption"),
    (47, "rate_limiter.py",        2, "adaptive rate limiting", "Add adaptive rate limiting that adjusts based on 429 response frequency"),
    (48, "attn_funcs.py",          2, "attention weight matrices sum to 1.0", "Validate attention weight matrices sum to 1.0 along the key dimension before analysis"),
    (49, "model_loader.py",        2, "model checksum verification", "Add model checksum verification after loading to detect corrupted weight files"),
    (50, "prep_attn_cache.py",     2, "LRU eviction for attention cache", "Implement LRU eviction for attention cache to prevent unbounded memory growth"),
    # 10 VERY IMPORTANT
    (51, "sentence_scatter_and_ttests.py", 3, "Bonferroni correction", "Apply Bonferroni correction for multiple comparisons to avoid inflated significance in t-tests"),
    (52, "rollouts.py",            3, "deterministic seeding for rollout", "Add deterministic seeding for rollout generation to ensure reproducible experiment results"),
    (53, "supp.py",                3, "race condition in concurrent suppression", "Fix race condition in concurrent suppression score writes that causes data loss under parallelism"),
    (54, "logits_funcs.py",        3, "NaN propagation in logit computations", "Guard against NaN propagation in logit computations by adding explicit nan-checks before softmax"),
    (55, "ablation.py",            3, "Restore original model weights after ablation", "Restore original model weights after ablation study to prevent corrupted state in subsequent runs"),
    (56, "analysis.py",            3, "analysis input tensors are on the same device", "Validate that analysis input tensors are on the same device to prevent silent cross-device errors"),
    (57, "plot_suppression_matrix.py", 3, "Clamp suppression matrix values", "Clamp suppression matrix values to valid range before plotting to avoid misleading color scales"),
    (58, "attribution_benchmark.py", 3, "ground-truth comparison baseline", "Add ground-truth comparison baseline to attribution benchmarks to measure absolute accuracy"),
    (59, "kl_attribution.py",      3, "degenerate distributions in KL attribution", "Handle degenerate distributions in KL attribution to prevent infinite divergence values"),
    (60, "provider_config.py",     3, "Encrypt stored API keys at rest", "Encrypt stored API keys at rest and decrypt only during active provider sessions"),

    # ── nanochat/ planted TODOs (IDs 61–90) ──
    # 10 plain
    (61, "checkpoint_manager.py",  1, "disk space check before writing", "Add disk space check before writing checkpoints to prevent partial saves on full volumes"),
    (62, "common.py",              1, "expected format of the configuration dictionary", "Document the expected format of the configuration dictionary with inline examples"),
    (63, "dataloader.py",          1, "skip malformed records", "Add option to skip malformed records instead of crashing the entire data loading pipeline"),
    (64, "dataset.py",             1, "token count and sequence length distribution", "Log dataset statistics such as token count and sequence length distribution at load time"),
    (65, "report.py",              1, "wall-clock training time", "Include wall-clock training time in generated report summaries"),
    (66, "chat_cli.py",            1, "command history persistence", "Add command history persistence across chat CLI sessions using readline history file"),
    (67, "tok_eval.py",            1, "per-category tokenizer evaluation", "Print per-category tokenizer evaluation scores in addition to the aggregate score"),
    (68, "common.py",              1, "dry-run mode that validates task", "Add a dry-run mode that validates task configuration without executing evaluation"),
    (69, "gsm8k.py",               1, "Strip whitespace from extracted numeric", "Strip whitespace from extracted numeric answers before comparison to reduce false negatives"),
    (70, "spellingbee.py",         1, "Cache the valid word dictionary", "Cache the valid word dictionary in memory to avoid repeated file reads during scoring"),
    # 10 IMPORTANT
    (71, "core_eval.py",           2, "per-sample evaluation results", "Save per-sample evaluation results to enable post-hoc error analysis on individual examples"),
    (72, "engine.py",              2, "gradient norm monitoring", "Add gradient norm monitoring and alert when gradient norms exceed a configurable threshold"),
    (73, "execution.py",           2, "graceful shutdown that saves current training", "Implement graceful shutdown that saves current training state on SIGTERM before exiting"),
    (74, "flash_attention.py",     2, "fallback to standard attention", "Add fallback to standard attention when flash attention is unavailable on the current hardware"),
    (75, "gpt.py",                 2, "pretrained weights match the current model", "Validate that loaded pretrained weights match the current model architecture dimensions"),
    (76, "optim.py",               2, "warmup steps do not exceed total training", "Add learning rate warmup validation to ensure warmup steps do not exceed total training steps"),
    (77, "base_train.py",          2, "mixed-precision fallback when FP16", "Implement automatic mixed-precision fallback when FP16 training encounters NaN losses"),
    (78, "chat_eval.py",           2, "timeout per evaluation sample", "Add timeout per evaluation sample to prevent hanging on degenerate model outputs"),
    (79, "chat_sft.py",            2, "SFT training data contains both instruction", "Validate that SFT training data contains both instruction and response fields before training starts"),
    (80, "humaneval.py",           2, "sandboxed subprocess to prevent unsafe code", "Run generated code in a sandboxed subprocess to prevent unsafe code execution during evaluation"),
    # 10 VERY IMPORTANT
    (81, "fp8.py",                 3, "overflow detection for FP8 quantization", "Add overflow detection for FP8 quantization to prevent silent precision loss in model weights"),
    (82, "loss_eval.py",           3, "division by zero in loss normalization", "Guard against division by zero in loss normalization when batch contains only padding tokens"),
    (83, "tokenizer.py",           3, "vocabulary size matches model embedding", "Validate that tokenizer vocabulary size matches model embedding dimensions at initialization"),
    (84, "base_eval.py",           3, "same device as the model to prevent silent CPU", "Ensure evaluation runs on the same device as the model to prevent silent CPU fallback on metrics"),
    (85, "chat_rl.py",             3, "Clip reward values to a bounded range", "Clip reward values to a bounded range to prevent reward hacking from destabilizing RL training"),
    (86, "chat_web.py",            3, "Sanitize all user-submitted chat inputs", "Sanitize all user-submitted chat inputs to prevent prompt injection and XSS in the web interface"),
    (87, "tok_train.py",           3, "training corpus character coverage", "Verify training corpus character coverage before tokenizer training to detect encoding errors early"),
    (88, "arc.py",                 3, "ARC answer choices are non-empty and unique", "Validate that ARC answer choices are non-empty and unique before running evaluation"),
    (89, "mmlu.py",                3, "few-shot examples come from a different split", "Ensure MMLU few-shot examples come from a different split than the test set to prevent data leakage"),
    (90, "gen_synthetic_data.py",  3, "deduplication check on generated synthetic", "Add deduplication check on generated synthetic samples to prevent train-test contamination"),

    # ── Pre-existing TODOs (IDs 91–98) ──
    # level 0 = pre-existing (not planted by us, no importance marker)
    # thought-anchors: 1
    (91, "supp.py",                0, "TODO: test", "test"),
    # nanochat: 7
    (92, "spellingbee.py",         0, "simulate cute little mistakes", "This is where the fun starts, we could simulate cute little mistakes"),
    (93, "smoltalk.py",            0, "remove these asserts later", "we could remove these asserts later, for now just don't want any footguns"),
    (94, "tokenizer.py",           0, "slightly inefficient here", "slightly inefficient here? :( hmm"),
    (95, "tokenizer.py",           0, "TODO: same", "same"),
    (96, "gpt.py",                 0, "bump base theta more", "bump base theta more? e.g. 100K is more common more recently"),
    (97, "gpt.py",                 0, "chunked cross-entropy", "experiment with chunked cross-entropy?"),
    (98, "chat_eval.py",           0, "remake the way this works", "remake the way this works"),
]

LEVEL_NAMES = {0: "pre-existing", 1: "plain", 2: "IMPORTANT", 3: "VERY IMPORTANT"}


def extract_all_agent_text(trajectory: dict) -> str:
    """Concatenate all agent messages for TODO mention checking."""
    return "\n".join(
        step.get("message", "") or ""
        for step in trajectory["steps"]
        if step.get("source") == "agent"
    )


def extract_tool_sequence(trajectory: dict) -> list:
    """Extract ordered list of tool calls with step info."""
    calls = []
    for step in trajectory["steps"]:
        for tc in step.get("tool_calls", []):
            calls.append({
                "step_id": step["step_id"],
                "tool": tc["function_name"],
                "args": tc.get("arguments", {}),
            })
    return calls


def check_todo_found(todo_id: int, snippet: str, full_text: str, text: str) -> bool:
    """Check if a specific TODO was mentioned in a block of text."""
    if snippet.lower() in text.lower():
        return True
    words = full_text.split()
    for i in range(len(words) - 3):
        chunk = " ".join(words[i:i+4])
        if chunk.lower() in text.lower():
            return True
    return False


def determine_discovery_order(trajectory: dict) -> dict:
    """
    Determine the order in which files were read (and thus TODOs discovered).
    Returns {file_short: discovery_step_id}.
    """
    file_order = {}
    for step in trajectory["steps"]:
        for tc in step.get("tool_calls", []):
            if tc["function_name"] == "Read":
                fpath = tc.get("arguments", {}).get("file_path", "")
                fname = Path(fpath).name
                if fname not in file_order:
                    file_order[fname] = step["step_id"]
    return file_order


# ── Compaction epoch tracking ──

def load_compaction_events(run_dir: Path) -> list:
    """Load compaction events from api_captures.jsonl.

    Returns list of dicts with keys:
        request_index, message_count_before, message_count_after,
        compacted_messages (post-compaction), pre_compaction_messages,
        pre_compaction_timestamp, activity_at_compaction
    """
    api_cap_path = run_dir / "session_01" / "api_captures.jsonl"
    if not api_cap_path.exists():
        return []

    events = []
    prev_count = 0
    for line in api_cap_path.read_text().strip().split("\n"):
        if not line.strip():
            continue
        cap = json.loads(line)
        if cap.get("is_compaction"):
            events.append({
                "request_index": cap.get("request_index"),
                "message_count_before": cap.get("pre_compaction_message_count", prev_count),
                "message_count_after": cap.get("message_count", 0),
                "compacted_messages": cap.get("compacted_messages", []),
                "pre_compaction_messages": cap.get("pre_compaction_messages"),
                "pre_compaction_timestamp": cap.get("pre_compaction_timestamp"),
                "activity_at_compaction": cap.get("activity_at_compaction", {}),
                "timestamp": cap.get("timestamp"),
            })
        prev_count = cap.get("message_count", prev_count)
    return events


def find_step_at_timestamp(trajectory: dict, timestamp_iso: str) -> int | None:
    """Find the trajectory step_id whose timestamp is closest to and <= the given timestamp."""
    from datetime import datetime as _dt

    try:
        target = _dt.fromisoformat(timestamp_iso)
    except (ValueError, TypeError):
        return None

    best_step_id = None
    best_diff = None

    for step in trajectory["steps"]:
        step_ts_str = step.get("timestamp")
        if not step_ts_str:
            continue
        try:
            step_ts = _dt.fromisoformat(step_ts_str)
        except (ValueError, TypeError):
            continue
        diff = (target - step_ts).total_seconds()
        if diff >= 0 and (best_diff is None or diff < best_diff):
            best_diff = diff
            best_step_id = step["step_id"]

    return best_step_id


def compute_compaction_step_boundaries(
    trajectory: dict, compaction_events: list, api_cap_path: Path
) -> list:
    """Determine the step_id at which each compaction occurred.

    Uses pre_compaction_timestamp for accurate correlation when available,
    falls back to request_index-based counting.

    Returns sorted list of step_ids where compaction happened.
    """
    if not compaction_events:
        return []

    compaction_step_ids = []
    for evt in compaction_events:
        step_id = None
        # Prefer timestamp-based correlation
        ts = evt.get("pre_compaction_timestamp") or evt.get("timestamp")
        if ts:
            step_id = find_step_at_timestamp(trajectory, ts)

        # Fallback: message_count heuristic
        if step_id is None:
            msg_count = evt.get("message_count_before", 0)
            approx_turn = msg_count // 2
            agent_step_ids = [
                s["step_id"] for s in trajectory["steps"]
                if s.get("source") == "agent" and (s.get("message") or s.get("tool_calls"))
            ]
            if approx_turn < len(agent_step_ids):
                step_id = agent_step_ids[approx_turn]
            elif agent_step_ids:
                step_id = agent_step_ids[-1]

        if step_id is not None:
            compaction_step_ids.append(step_id)

    return sorted(compaction_step_ids)


def compute_compaction_loss(pre_messages: list | None, post_messages: list) -> dict:
    """Compare pre- and post-compaction messages to quantify information loss."""
    if not pre_messages or not post_messages:
        return {"pre_chars": 0, "post_chars": 0, "compression_ratio": 0,
                "pre_message_count": 0, "post_message_count": 0}

    pre_text = json.dumps(pre_messages, default=str)
    post_text = json.dumps(post_messages, default=str)

    return {
        "pre_chars": len(pre_text),
        "post_chars": len(post_text),
        "compression_ratio": len(post_text) / len(pre_text) if len(pre_text) > 0 else 0,
        "pre_message_count": len(pre_messages),
        "post_message_count": len(post_messages),
    }


def assign_discovery_epoch(discovery_step: int | None, compaction_step_ids: list) -> int:
    """Determine which epoch a TODO was discovered in.

    Epoch 0 = before any compaction
    Epoch 1 = after compaction 1 but before compaction 2
    Epoch N = after compaction N

    If discovery_step is None (file not read), returns -1.
    """
    if discovery_step is None:
        return -1
    epoch = 0
    for boundary in compaction_step_ids:
        if discovery_step > boundary:
            epoch += 1
        else:
            break
    return epoch


def check_todo_in_compacted_context(
    snippet: str, full_text: str, compacted_messages: list
) -> bool:
    """Check if a TODO snippet appears in the post-compaction messages.

    The compacted_messages is the raw messages array sent in the API request
    after compaction. We serialize it to text and search.
    """
    if not compacted_messages:
        return False
    text = json.dumps(compacted_messages, default=str).lower()
    if snippet.lower() in text:
        return True
    words = full_text.split()
    for i in range(len(words) - 3):
        chunk = " ".join(words[i:i+4])
        if chunk.lower() in text:
            return True
    return False


def analyze_rep(run_dir: Path) -> dict:
    """Analyze a single rep's trajectory with epoch tracking."""
    traj_path = run_dir / "session_01" / "trajectory.json"
    meta_path = run_dir / "run_meta.json"
    api_cap_path = run_dir / "session_01" / "api_captures.jsonl"

    if not traj_path.exists():
        return {"error": f"No trajectory at {traj_path}"}

    trajectory = json.loads(traj_path.read_text())
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}

    all_agent_text = extract_all_agent_text(trajectory)
    tool_calls = extract_tool_sequence(trajectory)
    discovery_order = determine_discovery_order(trajectory)

    # Compaction events from proxy
    session_meta = meta.get("sessions", [{}])[0] if meta.get("sessions") else {}
    compaction_count = session_meta.get("compaction_count", 0)
    compaction_events = load_compaction_events(run_dir)

    # Compute step boundaries for each compaction
    compaction_step_ids = compute_compaction_step_boundaries(
        trajectory, compaction_events, api_cap_path
    )

    num_epochs = len(compaction_step_ids) + 1  # epoch 0 through N

    # Check each TODO
    results = []
    for todo_id, file_short, level, snippet, full_text in GROUND_TRUTH:
        found = check_todo_found(todo_id, snippet, full_text, all_agent_text)
        disc_step = discovery_order.get(file_short)
        file_was_read = file_short in discovery_order
        discovery_epoch = assign_discovery_epoch(disc_step, compaction_step_ids)

        # For each compaction event, check if this TODO survived into the
        # post-compaction context
        survived_compactions = []
        for i, evt in enumerate(compaction_events):
            survived = check_todo_in_compacted_context(
                snippet, full_text, evt.get("compacted_messages", [])
            )
            survived_compactions.append(survived)

        # Compute how many compactions this TODO had to survive
        # (only relevant if discovered before that compaction)
        compactions_faced = 0
        compactions_survived = 0
        for i, boundary in enumerate(compaction_step_ids):
            if disc_step is not None and disc_step <= boundary:
                compactions_faced += 1
                if i < len(survived_compactions) and survived_compactions[i]:
                    compactions_survived += 1

        results.append({
            "todo_id": todo_id,
            "file": file_short,
            "level": level,
            "level_name": LEVEL_NAMES[level],
            "snippet": snippet,
            "found_in_summary": found,
            "file_was_read": file_was_read,
            "discovery_step": disc_step,
            "discovery_epoch": discovery_epoch,
            "compactions_faced": compactions_faced,
            "compactions_survived": compactions_survived,
            "survived_each_compaction": survived_compactions,
        })

    grep_attempts = [tc for tc in tool_calls if tc["tool"] == "Grep"]

    return {
        "run_name": run_dir.name,
        "total_steps": len(trajectory["steps"]),
        "total_tool_calls": len(tool_calls),
        "tool_calls": tool_calls,
        "compaction_count": max(compaction_count, len(compaction_events)),
        "compaction_events": compaction_events,
        "compaction_step_ids": compaction_step_ids,
        "num_epochs": num_epochs,
        "grep_attempts": len(grep_attempts),
        "files_read": len(discovery_order),
        "discovery_order": discovery_order,
        "todo_results": results,
        "summary_length": len(all_agent_text),
        "cost_usd": session_meta.get("total_cost_usd", 0),
    }


def print_report(all_results: list):
    """Print full analysis report."""
    print("=" * 80)
    print("TODO COMPACTION EXPERIMENT — ANALYSIS REPORT")
    print("=" * 80)
    print()

    # ── Per-rep overview ──
    print("── Per-Rep Overview ──")
    print(f"{'Rep':<8} {'Steps':>6} {'Tools':>6} {'Files':>6} {'Grep?':>6} {'Compact':>8} {'Cost':>8} {'Found':>6} {'Missed':>7}")
    print("-" * 72)
    for r in all_results:
        found = sum(1 for t in r["todo_results"] if t["found_in_summary"])
        missed = len(GROUND_TRUTH) - found
        print(f"{r['run_name'][-4:]:<8} {r['total_steps']:>6} {r['total_tool_calls']:>6} "
              f"{r['files_read']:>6} {r['grep_attempts']:>6} {r['compaction_count']:>8} "
              f"${r['cost_usd']:>7.4f} {found:>6} {missed:>7}")
    print()

    # ── Recall by importance level ──
    print("── Recall by Importance Level (across all reps) ──")
    for level in [3, 2, 1, 0]:
        level_name = LEVEL_NAMES[level]
        level_todos = [t for r in all_results for t in r["todo_results"] if t["level"] == level]
        found_count = sum(1 for t in level_todos if t["found_in_summary"])
        total_count = len(level_todos)
        pct = (found_count / total_count * 100) if total_count > 0 else 0
        print(f"  {level_name:>15}: {found_count}/{total_count} ({pct:.0f}%)")
    print()

    # ── Per-rep recall by level ──
    print("── Per-Rep Recall by Level ──")
    print(f"{'Rep':<8} {'VERY IMP':>10} {'IMPORTANT':>10} {'plain':>10} {'pre-exist':>10} {'Total':>10}")
    print("-" * 60)
    for r in all_results:
        by_level = defaultdict(lambda: {"found": 0, "total": 0})
        for t in r["todo_results"]:
            by_level[t["level"]]["total"] += 1
            if t["found_in_summary"]:
                by_level[t["level"]]["found"] += 1
        total_found = sum(v["found"] for v in by_level.values())
        print(f"{r['run_name'][-4:]:<8} "
              f"{by_level[3]['found']}/{by_level[3]['total']:>2}       "
              f"{by_level[2]['found']}/{by_level[2]['total']:>2}       "
              f"{by_level[1]['found']}/{by_level[1]['total']:>2}       "
              f"{by_level[0]['found']}/{by_level[0]['total']:>2}        "
              f"{total_found}/{len(GROUND_TRUTH)}")
    print()

    # ── Recall by directory ──
    print("── Recall by Directory (across all reps) ──")
    dir_ranges = [("codi/", 1, 15), ("gen_latent_prior/", 16, 30), ("thought-anchors/", 31, 60), ("nanochat/", 61, 90), ("pre-existing", 91, 98)]
    for dir_name, lo, hi in dir_ranges:
        dir_todos = [t for r in all_results for t in r["todo_results"] if lo <= t["todo_id"] <= hi]
        found_count = sum(1 for t in dir_todos if t["found_in_summary"])
        total_count = len(dir_todos)
        pct = (found_count / total_count * 100) if total_count > 0 else 0
        print(f"  {dir_name:<20}: {found_count}/{total_count} ({pct:.0f}%)")
    print()

    # ── Per-TODO recall across reps ──
    print("── Per-TODO Recall (across all reps) ──")
    print(f"{'ID':>3} {'Level':>14} {'File':<28} {'Found':>8} {'Snippet'}")
    print("-" * 100)
    for todo_id, file_short, level, snippet, full_text in GROUND_TRUTH:
        found_count = sum(
            1 for r in all_results
            for t in r["todo_results"]
            if t["todo_id"] == todo_id and t["found_in_summary"]
        )
        level_name = LEVEL_NAMES[level]
        print(f"{todo_id:>3} {level_name:>14} {file_short:<28} {found_count}/{len(all_results):>5} {snippet[:50]}")
    print()

    # ── Discovery order analysis ──
    print("── File Discovery Order per Rep ──")
    for r in all_results:
        order = sorted(r["discovery_order"].items(), key=lambda x: x[1])
        print(f"  {r['run_name'][-4:]}: ", end="")
        if order:
            print(" -> ".join(f"{f}(step {s})" for f, s in order))
        else:
            print("(no files read)")
    print()

    # ── Tool usage patterns ──
    print("── Tool Usage per Rep ──")
    for r in all_results:
        tool_counts = defaultdict(int)
        for tc in r["tool_calls"]:
            tool_counts[tc["tool"]] += 1
        tools_str = ", ".join(f"{k}={v}" for k, v in sorted(tool_counts.items()))
        print(f"  {r['run_name'][-4:]}: {tools_str}")
    print()

    # ── Compaction timeline ──
    print("── Compaction Timeline ──")
    any_compaction = False
    for r in all_results:
        if r["compaction_count"] > 0 or r["compaction_events"]:
            any_compaction = True
            print(f"  {r['run_name']}: {r['compaction_count']} compaction(s), {r['num_epochs']} epoch(s)")
            for i, evt in enumerate(r["compaction_events"]):
                before = evt.get("message_count_before", "?")
                after = evt.get("message_count_after", "?")
                step_id = r["compaction_step_ids"][i] if i < len(r["compaction_step_ids"]) else "?"
                print(f"    Compaction {i+1}: messages {before} → {after}, ~step {step_id}")
    if not any_compaction:
        print("  No compaction events detected in any rep.")
    print()

    # ── Activity at compaction time ──
    if any_compaction:
        print("── Activity at Compaction Time ──")
        for r in all_results:
            if not r["compaction_events"]:
                continue
            print(f"  {r['run_name']}:")
            for i, evt in enumerate(r["compaction_events"]):
                activity = evt.get("activity_at_compaction", {})
                cls = activity.get("classification", "unknown")
                tools = activity.get("recent_tools", [])
                preview = activity.get("last_assistant_preview", "")[:80]
                loss = compute_compaction_loss(
                    evt.get("pre_compaction_messages"),
                    evt.get("compacted_messages", []),
                )
                ratio_str = f"{loss['compression_ratio']:.1%}" if loss["pre_chars"] > 0 else "n/a"
                print(f"    Compaction {i+1}: {cls} (tools: {tools})")
                print(f"      messages: {loss['pre_message_count']} → {loss['post_message_count']}, "
                      f"chars: {loss['pre_chars']:,} → {loss['post_chars']:,} ({ratio_str})")
                if preview:
                    print(f"      last msg: \"{preview}...\"")
        print()

        # ── Compaction loss summary ──
        print("── Compaction Loss Summary ──")
        all_ratios = []
        activity_counts = defaultdict(int)
        for r in all_results:
            for evt in r["compaction_events"]:
                loss = compute_compaction_loss(
                    evt.get("pre_compaction_messages"),
                    evt.get("compacted_messages", []),
                )
                if loss["pre_chars"] > 0:
                    all_ratios.append(loss["compression_ratio"])
                activity = evt.get("activity_at_compaction", {}).get("classification", "unknown")
                activity_counts[activity] += 1
        if all_ratios:
            print(f"  Mean compression ratio: {sum(all_ratios)/len(all_ratios):.1%}")
            print(f"  Min compression ratio:  {min(all_ratios):.1%}")
            print(f"  Max compression ratio:  {max(all_ratios):.1%}")
        print(f"  Activity distribution at compaction:")
        for act, count in sorted(activity_counts.items(), key=lambda x: -x[1]):
            print(f"    {act}: {count}")
        print()

    # ── Discovery epoch distribution ──
    print("── Discovery Epoch Distribution ──")
    print(f"{'Rep':<8}", end="")
    max_epochs = max((r["num_epochs"] for r in all_results), default=1)
    for e in range(max_epochs):
        print(f" {'Epoch '+str(e):>8}", end="")
    print(f" {'Not read':>9}")
    print("-" * (8 + 9 * max_epochs + 10))
    for r in all_results:
        epoch_counts = defaultdict(int)
        for t in r["todo_results"]:
            epoch_counts[t["discovery_epoch"]] += 1
        print(f"{r['run_name'][-4:]:<8}", end="")
        for e in range(max_epochs):
            print(f" {epoch_counts.get(e, 0):>8}", end="")
        print(f" {epoch_counts.get(-1, 0):>9}")
    print()

    # ── Compaction survival by importance level ──
    if any_compaction:
        print("── Compaction Survival by Importance Level ──")
        print("  (Of TODOs discovered BEFORE a compaction, how many survived in post-compaction context?)")
        print()
        for level in [3, 2, 1, 0]:
            level_name = LEVEL_NAMES[level]
            faced = 0
            survived = 0
            for r in all_results:
                for t in r["todo_results"]:
                    if t["level"] == level:
                        faced += t["compactions_faced"]
                        survived += t["compactions_survived"]
            pct = (survived / faced * 100) if faced > 0 else 0
            print(f"  {level_name:>15}: {survived}/{faced} compaction-survivals ({pct:.0f}%)")
        print()

        # ── Compaction survival by directory ──
        print("── Compaction Survival by Directory ──")
        dir_ranges = [("codi/", 1, 15), ("gen_latent_prior/", 16, 30), ("thought-anchors/", 31, 60), ("nanochat/", 61, 90), ("pre-existing", 91, 98)]
        for dir_name, lo, hi in dir_ranges:
            faced = 0
            survived = 0
            for r in all_results:
                for t in r["todo_results"]:
                    if lo <= t["todo_id"] <= hi:
                        faced += t["compactions_faced"]
                        survived += t["compactions_survived"]
            pct = (survived / faced * 100) if faced > 0 else 0
            print(f"  {dir_name:<20}: {survived}/{faced} ({pct:.0f}%)")
        print()

        # ── Per-compaction-round survival matrix ──
        print("── Per-Compaction-Round Survival Matrix ──")
        print("  (How many TODOs survived each specific compaction round?)")
        print()
        for r in all_results:
            if not r["compaction_events"]:
                continue
            print(f"  {r['run_name']}:")
            for i in range(len(r["compaction_events"])):
                # Count TODOs that existed before this compaction
                todos_before = [t for t in r["todo_results"]
                                if t["discovery_epoch"] >= 0
                                and (i < len(r["compaction_step_ids"])
                                     and (t["discovery_step"] or 0) <= r["compaction_step_ids"][i])]
                survived = sum(1 for t in todos_before
                               if i < len(t["survived_each_compaction"]) and t["survived_each_compaction"][i])
                total_before = len(todos_before)
                pct = (survived / total_before * 100) if total_before > 0 else 0
                print(f"    Round {i+1}: {survived}/{total_before} survived ({pct:.0f}%)")
            print()

        # ── Survival rate by discovery epoch ──
        print("── Final Recall by Discovery Epoch ──")
        print("  (Of TODOs discovered in epoch N, how many appear in the final summary?)")
        print()
        epoch_recall = defaultdict(lambda: {"found": 0, "total": 0})
        for r in all_results:
            for t in r["todo_results"]:
                ep = t["discovery_epoch"]
                epoch_recall[ep]["total"] += 1
                if t["found_in_summary"]:
                    epoch_recall[ep]["found"] += 1
        for ep in sorted(epoch_recall.keys()):
            d = epoch_recall[ep]
            pct = (d["found"] / d["total"] * 100) if d["total"] > 0 else 0
            label = f"Epoch {ep}" if ep >= 0 else "Not read"
            print(f"  {label:<12}: {d['found']}/{d['total']} ({pct:.0f}%)")
        print()

        # ── Cross-tabulation: discovery epoch × importance level ──
        print("── Cross-Tab: Discovery Epoch × Importance Level (Final Recall) ──")
        print(f"  {'Epoch':<10}", end="")
        for level in [3, 2, 1, 0]:
            print(f" {LEVEL_NAMES[level]:>15}", end="")
        print()
        print("  " + "-" * (10 + 16 * 4))
        cross = defaultdict(lambda: defaultdict(lambda: {"found": 0, "total": 0}))
        for r in all_results:
            for t in r["todo_results"]:
                cross[t["discovery_epoch"]][t["level"]]["total"] += 1
                if t["found_in_summary"]:
                    cross[t["discovery_epoch"]][t["level"]]["found"] += 1
        for ep in sorted(cross.keys()):
            label = f"Epoch {ep}" if ep >= 0 else "Not read"
            print(f"  {label:<10}", end="")
            for level in [3, 2, 1, 0]:
                d = cross[ep][level]
                if d["total"] > 0:
                    pct = d["found"] / d["total"] * 100
                    print(f" {d['found']}/{d['total']:>2} ({pct:>3.0f}%){' ':>3}", end="")
                else:
                    print(f" {'—':>15}", end="")
            print()
        print()

        # ── Most-dropped TODOs ──
        print("── TODOs Most Frequently Dropped After Compaction ──")
        print("  (TODOs that faced compaction but had low survival or low final recall)")
        drop_info = []
        for todo_id, file_short, level, snippet, full_text in GROUND_TRUTH:
            total_faced = 0
            total_survived = 0
            times_found = 0
            for r in all_results:
                for t in r["todo_results"]:
                    if t["todo_id"] == todo_id:
                        total_faced += t["compactions_faced"]
                        total_survived += t["compactions_survived"]
                        if t["found_in_summary"]:
                            times_found += 1
            if total_faced > 0:
                surv_rate = total_survived / total_faced
                drop_info.append((todo_id, file_short, LEVEL_NAMES[level], snippet,
                                  total_faced, total_survived, surv_rate, times_found))
        drop_info.sort(key=lambda x: (x[6], x[7]))  # worst survival first
        print(f"  {'ID':>3} {'Level':>14} {'File':<25} {'Survived':>10} {'Found':>6} {'Snippet'}")
        print("  " + "-" * 100)
        for todo_id, fshort, lname, snip, faced, survived, srate, found in drop_info[:20]:
            print(f"  {todo_id:>3} {lname:>14} {fshort:<25} {survived}/{faced:>2} ({srate:>4.0%}) "
                  f"{found}/{len(all_results):>2}    {snip[:40]}")
        print()

    # ── Summary statistics ──
    all_found = [sum(1 for t in r["todo_results"] if t["found_in_summary"]) for r in all_results]
    print("── Summary Statistics ──")
    print(f"  Reps:              {len(all_results)}")
    n = len(GROUND_TRUTH)
    print(f"  Mean TODOs found:  {sum(all_found)/len(all_found):.1f} / {n}")
    print(f"  Min TODOs found:   {min(all_found)} / {n}")
    print(f"  Max TODOs found:   {max(all_found)} / {n}")
    print(f"  Total cost:        ${sum(r['cost_usd'] for r in all_results):.4f}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Analyze TODO compaction experiment results")
    parser.add_argument("--runs-dir", default="runs", help="Directory containing run outputs")
    parser.add_argument("--prefix", default="canary-todo-compaction-rep", help="Run name prefix")
    parser.add_argument("--json-output", help="Optional: save raw results to JSON file")
    args = parser.parse_args()

    runs_dir = Path(args.runs_dir)
    # Find all matching run directories
    rep_dirs = sorted(runs_dir.glob(f"{args.prefix}*"))

    if not rep_dirs:
        print(f"No runs found matching {runs_dir}/{args.prefix}*")
        return 1

    print(f"Found {len(rep_dirs)} reps: {[d.name for d in rep_dirs]}")
    print()

    all_results = []
    for rd in rep_dirs:
        result = analyze_rep(rd)
        if "error" in result:
            print(f"  WARN: {rd.name}: {result['error']}")
        else:
            all_results.append(result)

    if not all_results:
        print("No valid results to analyze.")
        return 1

    print_report(all_results)

    if args.json_output:
        Path(args.json_output).write_text(json.dumps(all_results, indent=2, default=str))
        print(f"Raw results saved to {args.json_output}")

    return 0


if __name__ == "__main__":
    exit(main())
