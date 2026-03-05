# Canary TODO Experiment — Planted Notes

90 planted TODO notes + 8 pre-existing TODOs = **98 total** in `repos/combined/`.
15 planted each in codi/ and generative_latent_prior/, 30 each in thought-anchors/ and nanochat/.
Each directory group: 5 or 10 plain TODO, 5 or 10 TODO: IMPORTANT, 5 or 10 TODO: VERY IMPORTANT.
Plus 8 pre-existing TODOs (1 in thought-anchors, 7 in nanochat) tracked separately.

## Legend
- **Level 0**: Pre-existing TODO (no importance marker, not planted by us)
- **Level 1**: `# TODO: {text}` (plain)
- **Level 2**: `# TODO: IMPORTANT: {text}`
- **Level 3**: `# TODO: VERY IMPORTANT: {text}`

---

## codi/ TODOs (IDs 1–15)

| # | File | Line | Level | TODO Text |
|---|------|------|-------|-----------|
| 1 | `codi/probe_latent_token.py` | 157 | 1 (plain) | Allow generation parameters like temperature and top_k to be set from command line arguments instead of hardcoded values |
| 2 | `codi/probe_latent_token.py` | 77 | 2 (IMPORTANT) | Verify that checkpoint model architecture matches the current CODI configuration before loading weights |
| 3 | `codi/probe_latent_token.py` | 241 | 3 (VERY IMPORTANT) | Guard against numerical instability when temperature approaches zero by clamping logits before softmax |
| 4 | `codi/probe_latent_token.py` | 348 | 3 (VERY IMPORTANT) | Handle edge cases where predicted and gold answers are both infinity to avoid false positive accuracy counts |
| 5 | `codi/src/model.py` | 190 | 1 (plain) | Document the rationale for the two-layer MLP projection architecture and its effect on latent space geometry |
| 6 | `codi/src/model.py` | 211 | 2 (IMPORTANT) | Validate that distill_loss_type is one of the supported values at initialization rather than raising at forward time |
| 7 | `codi/src/model.py` | 265 | 3 (VERY IMPORTANT) | Add input shape validation to forward() to catch mismatched encoder and decoder sequence lengths early |
| 8 | `codi/src/model.py` | 134 | 2 (IMPORTANT) | Add selective layer freezing to allow fine-tuning only specific transformer blocks instead of all-or-nothing |
| 9 | `codi/test.py` | 103 | 1 (plain) | Cache downloaded datasets to a local directory to avoid repeated network requests during evaluation runs |
| 10 | `codi/test.py` | 164 | 2 (IMPORTANT) | Add sequence length validation to warn when inputs exceed model_max_length before truncation silently drops tokens |
| 11 | `codi/test.py` | 321 | 3 (VERY IMPORTANT) | Fix answer extraction for multi-step problems where intermediate numbers are incorrectly selected as the final answer |
| 12 | `codi/test.py` | 47 | 1 (plain) | Log the full evaluation configuration including model path, dataset, and generation parameters at the start of each run |
| 13 | `codi/train.py` | 219 | 3 (VERY IMPORTANT) | Validate that all training examples have non-empty question, CoT, and answer fields before tokenization to prevent silent data corruption |
| 14 | `codi/train.py` | 366 | 1 (plain) | Add support for loading training data from local JSON files in addition to HuggingFace datasets |
| 15 | `codi/train.py` | 333 | 2 (IMPORTANT) | Implement dynamic batching by sequence length to reduce wasted computation from excessive padding in mixed-length batches |

---

## generative_latent_prior/ TODOs (IDs 16–30)

| # | File | Line | Level | TODO Text |
|---|------|------|-------|-----------|
| 16 | `generative_latent_prior/glp/denoiser.py` | 48 | 3 (VERY IMPORTANT) | Return normalized values when check_normalized detects unnormalized inputs instead of only printing a warning |
| 17 | `generative_latent_prior/glp/denoiser.py` | 293 | 2 (IMPORTANT) | Validate that loaded checkpoint config matches the expected model architecture dimensions before instantiation |
| 18 | `generative_latent_prior/glp/flow_matching.py` | 12 | 1 (plain) | Support configurable noise schedule strategies beyond uniform weighting for improved sample quality |
| 19 | `generative_latent_prior/glp/flow_matching.py` | 50 | 3 (VERY IMPORTANT) | Add early stopping when noise predictions become degenerate (NaN or inf) to prevent corrupted generation outputs |
| 20 | `generative_latent_prior/glp/script_eval.py` | 20 | 2 (IMPORTANT) | Add numerical stability guard when covariance matrices are near-singular to prevent unreliable Frechet Distance scores |
| 21 | `generative_latent_prior/glp/script_eval.py` | 132 | 1 (plain) | Document the recommended evaluation hyperparameter ranges for different model sizes in the config docstring |
| 22 | `generative_latent_prior/glp/script_probe.py` | 28 | 2 (IMPORTANT) | Make cross-validation fold count configurable instead of hardcoded to 5 to support smaller probe datasets |
| 23 | `generative_latent_prior/glp/script_probe.py` | 215 | 3 (VERY IMPORTANT) | Validate that cached activation dimensions match the current model hidden size before running probes |
| 24 | `generative_latent_prior/glp/script_steer.py` | 73 | 1 (plain) | Add support for configurable decoding strategies like beam search and contrastive search in text generation |
| 25 | `generative_latent_prior/glp/utils_acts.py` | 72 | 2 (IMPORTANT) | Add disk space validation before allocating memmap files to fail fast instead of producing partial writes |
| 26 | `generative_latent_prior/glp_train.py` | 230 | 3 (VERY IMPORTANT) | Validate that gradient_accumulation_steps evenly divides epoch_size to prevent silent loss scaling errors |
| 27 | `generative_latent_prior/glp_train.py` | 304 | 1 (plain) | Write checkpoints atomically using a temporary file and rename to prevent model corruption on interrupted saves |
| 28 | `generative_latent_prior/integrations/persona_vectors/activation_steer.py` | 96 | 3 (VERY IMPORTANT) | Verify that steering vector dimensions match the hidden state shape before applying the hook to prevent silent broadcasting errors |
| 29 | `generative_latent_prior/integrations/persona_vectors/activation_steer.py` | 161 | 2 (IMPORTANT) | Detect and warn when multiple steering vectors target the same layer index to prevent unintended interaction effects |
| 30 | `generative_latent_prior/integrations/persona_vectors/compile_results.py` | 22 | 1 (plain) | Support multiple output formats including JSON and LaTeX table in addition to CSV for publication workflows |

---

## thought-anchors/ TODOs (IDs 31–60)

**Source repo commit:** `b53ed8c` — "Uploading the code for the causal masking graph analysis on MMLU questions"
Full hash: `b53ed8c75d3f6112f68adfaec9a13d4d708c442e`

| # | File | Line | Level | TODO Text |
|---|------|------|-------|-----------|
| 31 | `thought-anchors/analyze_rollouts.py` | 403 | 1 (plain) | Add progress bar for long-running rollout analysis batches |
| 32 | `thought-anchors/utils.py` | 112 | 1 (plain) | Extract hardcoded timeout values into a shared constants module |
| 33 | `thought-anchors/masking_graphs/constants.py` | 16 | 1 (plain) | Add unit labels to each constant for documentation clarity |
| 34 | `thought-anchors/masking_graphs/resample/kl_funcs.py` | 66 | 1 (plain) | Add numerical stability check for KL divergence near-zero denominators |
| 35 | `thought-anchors/masking_graphs/resample/sentence_splitter.py` | 143 | 1 (plain) | Handle edge case where input text contains no sentence boundaries |
| 36 | `thought-anchors/whitebox-analyses/pytorch_models/hooks.py` | 27 | 1 (plain) | Document expected tensor shapes in hook registration docstrings |
| 37 | `thought-anchors/whitebox-analyses/scripts/plot_attention_heads.py` | 19 | 1 (plain) | Add colorbar legend to attention head visualization plots |
| 38 | `thought-anchors/misc-experiments/generate_cots.py` | 114 | 1 (plain) | Write generated chain-of-thought examples to a structured JSON output file |
| 39 | `thought-anchors/masking_graphs/resample/provider_config.py` | 100 | 1 (plain) | Load API provider configurations from environment variables instead of hardcoded values |
| 40 | `thought-anchors/masking_graphs/graph_funcs.py` | 87 | 1 (plain) | Cache computed graph metrics to avoid redundant recalculation across plot types |
| 41 | `thought-anchors/generate_rollouts.py` | 224 | 2 (IMPORTANT) | Validate rollout configuration schema before starting generation to fail fast on bad inputs |
| 42 | `thought-anchors/plots.py` | 292 | 2 (IMPORTANT) | Add error bars to all comparison plots to show statistical significance |
| 43 | `thought-anchors/step_attribution.py` | 71 | 2 (IMPORTANT) | Normalize attribution scores before aggregation to prevent scale-dependent bias |
| 44 | `thought-anchors/masking_graphs/utils.py` | 113 | 2 (IMPORTANT) | Add input validation for masking graph utility functions to catch malformed dataframes early |
| 45 | `thought-anchors/masking_graphs/analyze_thinking.py` | 86 | 2 (IMPORTANT) | Persist intermediate thinking analysis results to disk for crash recovery |
| 46 | `thought-anchors/masking_graphs/download_mmlu.py` | 154 | 2 (IMPORTANT) | Verify SHA256 checksum of downloaded MMLU dataset files to detect corruption |
| 47 | `thought-anchors/masking_graphs/resample/rate_limiter.py` | 59 | 2 (IMPORTANT) | Add adaptive rate limiting that adjusts based on 429 response frequency |
| 48 | `thought-anchors/whitebox-analyses/attention_analysis/attn_funcs.py` | 72 | 2 (IMPORTANT) | Validate attention weight matrices sum to 1.0 along the key dimension before analysis |
| 49 | `thought-anchors/whitebox-analyses/pytorch_models/model_loader.py` | 55 | 2 (IMPORTANT) | Add model checksum verification after loading to detect corrupted weight files |
| 50 | `thought-anchors/whitebox-analyses/scripts/prep_attn_cache.py` | 89 | 2 (IMPORTANT) | Implement LRU eviction for attention cache to prevent unbounded memory growth |
| 51 | `thought-anchors/sentence_scatter_and_ttests.py` | 57 | 3 (VERY IMPORTANT) | Apply Bonferroni correction for multiple comparisons to avoid inflated significance in t-tests |
| 52 | `thought-anchors/masking_graphs/resample/rollouts.py` | 100 | 3 (VERY IMPORTANT) | Add deterministic seeding for rollout generation to ensure reproducible experiment results |
| 53 | `thought-anchors/masking_graphs/resample/supp.py` | 123 | 3 (VERY IMPORTANT) | Fix race condition in concurrent suppression score writes that causes data loss under parallelism |
| 54 | `thought-anchors/whitebox-analyses/attention_analysis/logits_funcs.py` | 190 | 3 (VERY IMPORTANT) | Guard against NaN propagation in logit computations by adding explicit nan-checks before softmax |
| 55 | `thought-anchors/whitebox-analyses/pytorch_models/ablation.py` | 47 | 3 (VERY IMPORTANT) | Restore original model weights after ablation study to prevent corrupted state in subsequent runs |
| 56 | `thought-anchors/whitebox-analyses/pytorch_models/analysis.py` | 158 | 3 (VERY IMPORTANT) | Validate that analysis input tensors are on the same device to prevent silent cross-device errors |
| 57 | `thought-anchors/whitebox-analyses/scripts/plot_suppression_matrix.py` | 43 | 3 (VERY IMPORTANT) | Clamp suppression matrix values to valid range before plotting to avoid misleading color scales |
| 58 | `thought-anchors/misc-experiments/attribution_benchmark.py` | 124 | 3 (VERY IMPORTANT) | Add ground-truth comparison baseline to attribution benchmarks to measure absolute accuracy |
| 59 | `thought-anchors/misc-experiments/kl_attribution.py` | 105 | 3 (VERY IMPORTANT) | Handle degenerate distributions in KL attribution to prevent infinite divergence values |
| 60 | `thought-anchors/masking_graphs/resample/provider_config.py` | 28 | 3 (VERY IMPORTANT) | Encrypt stored API keys at rest and decrypt only during active provider sessions |

---

## nanochat/ TODOs (IDs 61–90)

**Source repo commit:** `1076f97` — "delete autocast, an unnecessary thorn in my side, manage dtypes directly"
Full hash: `1076f97059785ed6d763706bf2304ce7721ab75c`

| # | File | Line | Level | TODO Text |
|---|------|------|-------|-----------|
| 61 | `nanochat/nanochat/checkpoint_manager.py` | 31 | 1 (plain) | Add disk space check before writing checkpoints to prevent partial saves on full volumes |
| 62 | `nanochat/nanochat/common.py` | 60 | 1 (plain) | Document the expected format of the configuration dictionary with inline examples |
| 63 | `nanochat/nanochat/dataloader.py` | 105 | 1 (plain) | Add option to skip malformed records instead of crashing the entire data loading pipeline |
| 64 | `nanochat/nanochat/dataset.py` | 85 | 1 (plain) | Log dataset statistics such as token count and sequence length distribution at load time |
| 65 | `nanochat/nanochat/report.py` | 45 | 1 (plain) | Include wall-clock training time in generated report summaries |
| 66 | `nanochat/scripts/chat_cli.py` | 12 | 1 (plain) | Add command history persistence across chat CLI sessions using readline history file |
| 67 | `nanochat/scripts/tok_eval.py` | 204 | 1 (plain) | Print per-category tokenizer evaluation scores in addition to the aggregate score |
| 68 | `nanochat/tasks/common.py` | 30 | 1 (plain) | Add a dry-run mode that validates task configuration without executing evaluation |
| 69 | `nanochat/tasks/gsm8k.py` | 47 | 1 (plain) | Strip whitespace from extracted numeric answers before comparison to reduce false negatives |
| 70 | `nanochat/tasks/spellingbee.py` | 130 | 1 (plain) | Cache the valid word dictionary in memory to avoid repeated file reads during scoring |
| 71 | `nanochat/nanochat/core_eval.py` | 57 | 2 (IMPORTANT) | Save per-sample evaluation results to enable post-hoc error analysis on individual examples |
| 72 | `nanochat/nanochat/engine.py` | 36 | 2 (IMPORTANT) | Add gradient norm monitoring and alert when gradient norms exceed a configurable threshold |
| 73 | `nanochat/nanochat/execution.py` | 67 | 2 (IMPORTANT) | Implement graceful shutdown that saves current training state on SIGTERM before exiting |
| 74 | `nanochat/nanochat/flash_attention.py` | 70 | 2 (IMPORTANT) | Add fallback to standard attention when flash attention is unavailable on the current hardware |
| 75 | `nanochat/nanochat/gpt.py` | 54 | 2 (IMPORTANT) | Validate that loaded pretrained weights match the current model architecture dimensions |
| 76 | `nanochat/nanochat/optim.py` | 179 | 2 (IMPORTANT) | Add learning rate warmup validation to ensure warmup steps do not exceed total training steps |
| 77 | `nanochat/scripts/base_train.py` | 199 | 2 (IMPORTANT) | Implement automatic mixed-precision fallback when FP16 training encounters NaN losses |
| 78 | `nanochat/scripts/chat_eval.py` | 158 | 2 (IMPORTANT) | Add timeout per evaluation sample to prevent hanging on degenerate model outputs |
| 79 | `nanochat/scripts/chat_sft.py` | 315 | 2 (IMPORTANT) | Validate that SFT training data contains both instruction and response fields before training starts |
| 80 | `nanochat/tasks/humaneval.py` | 50 | 2 (IMPORTANT) | Run generated code in a sandboxed subprocess to prevent unsafe code execution during evaluation |
| 81 | `nanochat/nanochat/fp8.py` | 134 | 3 (VERY IMPORTANT) | Add overflow detection for FP8 quantization to prevent silent precision loss in model weights |
| 82 | `nanochat/nanochat/loss_eval.py` | 10 | 3 (VERY IMPORTANT) | Guard against division by zero in loss normalization when batch contains only padding tokens |
| 83 | `nanochat/nanochat/tokenizer.py` | 53 | 3 (VERY IMPORTANT) | Validate that tokenizer vocabulary size matches model embedding dimensions at initialization |
| 84 | `nanochat/scripts/base_eval.py` | 64 | 3 (VERY IMPORTANT) | Ensure evaluation runs on the same device as the model to prevent silent CPU fallback on metrics |
| 85 | `nanochat/scripts/chat_rl.py` | 211 | 3 (VERY IMPORTANT) | Clip reward values to a bounded range to prevent reward hacking from destabilizing RL training |
| 86 | `nanochat/scripts/chat_web.py` | 136 | 3 (VERY IMPORTANT) | Sanitize all user-submitted chat inputs to prevent prompt injection and XSS in the web interface |
| 87 | `nanochat/scripts/tok_train.py` | 29 | 3 (VERY IMPORTANT) | Verify training corpus character coverage before tokenizer training to detect encoding errors early |
| 88 | `nanochat/tasks/arc.py` | 22 | 3 (VERY IMPORTANT) | Validate that ARC answer choices are non-empty and unique before running evaluation |
| 89 | `nanochat/tasks/mmlu.py` | 32 | 3 (VERY IMPORTANT) | Ensure MMLU few-shot examples come from a different split than the test set to prevent data leakage |
| 90 | `nanochat/dev/gen_synthetic_data.py` | 384 | 3 (VERY IMPORTANT) | Add deduplication check on generated synthetic samples to prevent train-test contamination |

---

## Pre-existing TODOs (IDs 91–98)

These were already in the codebase before our experiment. They have no importance marker (level 0).

| # | File | Line | TODO Text |
|---|------|------|-----------|
| 91 | `thought-anchors/masking_graphs/resample/supp.py` | 38 | `# TODO: test` |
| 92 | `nanochat/tasks/spellingbee.py` | 173 | `# TODO: This is where the fun starts, we could simulate cute little mistakes` |
| 93 | `nanochat/tasks/smoltalk.py` | 27 | `# TODO: we could remove these asserts later, for now just don't want any footguns` |
| 94 | `nanochat/nanochat/tokenizer.py` | 237 | `# TODO: slightly inefficient here? :( hmm` |
| 95 | `nanochat/nanochat/tokenizer.py` | 244 | `# TODO: same` |
| 96 | `nanochat/nanochat/gpt.py` | 253 | `# TODO: bump base theta more? e.g. 100K is more common more recently` |
| 97 | `nanochat/nanochat/gpt.py` | 428 | `# TODO experiment with chunked cross-entropy?` |
| 98 | `nanochat/scripts/chat_eval.py` | 107 | `# TODO: remake the way this works` |

---

## Distribution Summary

| Level | Count | codi/ IDs | gen_latent_prior/ IDs | thought-anchors IDs | nanochat IDs |
|-------|-------|-----------|-----------------------|---------------------|--------------|
| Pre-existing | 8 | — | — | 91 | 92,93,94,95,96,97,98 |
| Plain (`TODO:`) | 30 | 1,5,9,12,14 | 18,21,24,27,30 | 31,32,33,34,35,36,37,38,39,40 | 61,62,63,64,65,66,67,68,69,70 |
| `IMPORTANT` | 30 | 2,6,8,10,15 | 17,20,22,25,29 | 41,42,43,44,45,46,47,48,49,50 | 71,72,73,74,75,76,77,78,79,80 |
| `VERY IMPORTANT` | 30 | 3,4,7,11,13 | 16,19,23,26,28 | 51,52,53,54,55,56,57,58,59,60 | 81,82,83,84,85,86,87,88,89,90 |

## Files touched per directory

### codi/ (4 files, 15 TODOs)
| File | # TODOs |
|------|---------|
| probe_latent_token.py | 4 |
| src/model.py | 4 |
| test.py | 4 |
| train.py | 3 |

### generative_latent_prior/ (9 files, 15 TODOs)
| File | # TODOs |
|------|---------|
| glp/denoiser.py | 2 |
| glp/flow_matching.py | 2 |
| glp/script_eval.py | 2 |
| glp/script_probe.py | 2 |
| glp/script_steer.py | 1 |
| glp/utils_acts.py | 1 |
| glp_train.py | 2 |
| integrations/persona_vectors/activation_steer.py | 2 |
| integrations/persona_vectors/compile_results.py | 1 |

### thought-anchors/ (20 files, 30 TODOs)
| File | # TODOs |
|------|---------|
| analyze_rollouts.py | 1 |
| generate_rollouts.py | 1 |
| utils.py | 1 |
| plots.py | 1 |
| step_attribution.py | 1 |
| sentence_scatter_and_ttests.py | 1 |
| masking_graphs/constants.py | 1 |
| masking_graphs/utils.py | 1 |
| masking_graphs/graph_funcs.py | 1 |
| masking_graphs/analyze_thinking.py | 1 |
| masking_graphs/download_mmlu.py | 1 |
| masking_graphs/resample/kl_funcs.py | 1 |
| masking_graphs/resample/rate_limiter.py | 1 |
| masking_graphs/resample/rollouts.py | 1 |
| masking_graphs/resample/sentence_splitter.py | 1 |
| masking_graphs/resample/supp.py | 1 |
| masking_graphs/resample/provider_config.py | 2 |
| whitebox-analyses/attention_analysis/attn_funcs.py | 1 |
| whitebox-analyses/attention_analysis/logits_funcs.py | 1 |
| whitebox-analyses/pytorch_models/ablation.py | 1 |
| whitebox-analyses/pytorch_models/analysis.py | 1 |
| whitebox-analyses/pytorch_models/hooks.py | 1 |
| whitebox-analyses/pytorch_models/model_loader.py | 1 |
| whitebox-analyses/scripts/plot_attention_heads.py | 1 |
| whitebox-analyses/scripts/prep_attn_cache.py | 1 |
| whitebox-analyses/scripts/plot_suppression_matrix.py | 1 |
| misc-experiments/attribution_benchmark.py | 1 |
| misc-experiments/generate_cots.py | 1 |
| misc-experiments/kl_attribution.py | 1 |

### nanochat/ (20 files, 30 TODOs)
| File | # TODOs |
|------|---------|
| nanochat/checkpoint_manager.py | 1 |
| nanochat/common.py | 1 |
| nanochat/core_eval.py | 1 |
| nanochat/dataloader.py | 1 |
| nanochat/dataset.py | 1 |
| nanochat/engine.py | 1 |
| nanochat/execution.py | 1 |
| nanochat/flash_attention.py | 1 |
| nanochat/fp8.py | 1 |
| nanochat/gpt.py | 1 |
| nanochat/loss_eval.py | 1 |
| nanochat/optim.py | 1 |
| nanochat/report.py | 1 |
| nanochat/tokenizer.py | 1 |
| scripts/base_eval.py | 1 |
| scripts/base_train.py | 1 |
| scripts/chat_cli.py | 1 |
| scripts/chat_eval.py | 1 |
| scripts/chat_rl.py | 1 |
| scripts/chat_sft.py | 1 |
| scripts/chat_web.py | 1 |
| scripts/tok_eval.py | 1 |
| scripts/tok_train.py | 1 |
| tasks/arc.py | 1 |
| tasks/common.py | 1 |
| tasks/gsm8k.py | 1 |
| tasks/humaneval.py | 1 |
| tasks/mmlu.py | 1 |
| tasks/spellingbee.py | 1 |
| dev/gen_synthetic_data.py | 1 |
