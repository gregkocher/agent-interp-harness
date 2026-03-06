# TODO: Improve Agent Identification in Capture Proxy

## Current Problem

The proxy (`src/harness/proxy.py`) needs to classify each API request as `main`, `subagent`, or `sdk_internal` to track compaction separately per context. Both existing approaches have flaws.

## Approach 1: `system_prompt_hash` (main branch)

- First request's system hash becomes the main agent fingerprint
- **Fails because**: Claude Code mutates the system prompt mid-session (cache control TTL changes, system reminders appended, etc.), causing the hash to change even though it's still the main agent
- Result: main agent requests get misclassified as subagent after any system prompt mutation
- **This is the worse of the two approaches** because system reminders (`<system-reminder>` tags) are injected automatically by Claude Code — not user-configured. They appear/disappear unpredictably (task tool reminders, skill availability notices, etc.), so the hash drifts routinely and silently.
- Consequences:
  - Compaction tracking splits mid-session — the proxy starts tracking two (or more) separate "agents" that are all actually the main agent, each with incomplete message count history
  - Real compaction events get missed — after a system prompt mutation, the "new" agent context has no prior message count baseline, so the next compaction has nothing to compare against
  - Every system prompt mutation looks like a new agent appearing — a single session can produce 5+ phantom "subagent" contexts

## Approach 2: `tools_hash` (memory-compaction-exps branch)

- First request's tools hash becomes the main agent fingerprint
- More stable since tool definitions don't change mid-session
- **Fails when**:
  - A subagent inherits all tools (`tools: null` in AgentConfig) → same tools_hash as main
  - Two different subagents have identical tool sets → can't distinguish them from each other
  - Custom agent configs that happen to match the main agent's tool set
- **This is the better of the two approaches** because the failure case is explicit and opt-in — it only triggers if someone configures `tools: null` on a subagent in their experiment YAML. Tool definitions don't mutate mid-session the way system prompts do.
- Consequences when it does fail (subagent with inherited tools):
  - Subagent spawn (message_count drops to 1) gets misread as a main agent compaction — **false positive compaction event**
  - Analysis of "what survived compaction" would actually be studying a subagent's fresh context, not compressed main agent context
  - Real main agent compaction could get masked if it happens while the proxy is confused about which context is which
- For current experiments (no custom subagents defined, Claude Code's built-in subagents use reduced tool sets), this approach works correctly

## Impact on Experiment Results

Misclassifying agents has one primary consequence: **corrupted compaction data**.
- False positive compaction: we capture a subagent spawn as if it were a compaction, polluting before/after analysis
- Missed compaction: we lose the before/after snapshot entirely for a real compaction event
- Split tracking: partial message count histories make it impossible to reconstruct the true compaction timeline

For experiments specifically studying compaction behavior (e.g., representation-decay, canary-todo-compaction), this directly undermines the data quality. For experiments that just use compaction count as metadata, the impact is minor.

## What's Available in Raw HTTP Requests

From analysis of `raw_dumps/`:

| Signal | Main Agent | Subagent | Reliable? |
|--------|-----------|----------|-----------|
| `tools` array | 18 tools (full set) | 9 tools (restricted) | Only if subagent has different tools |
| `system` prompt | User's system prompt | Subagent-specific prompt | Unstable (hash changes mid-session) |
| `metadata` | `{user_id: ...}` | Identical | No — same for all |
| HTTP headers | Standard SDK headers | Identical | No — no agent-identifying headers |
| `model` field | Config model | May differ (sonnet/haiku/opus) | Only if subagent uses different model |
| `message_count` | Grows over session | Starts at 1 | Ambiguous with compaction |

**Not available in HTTP layer**: agent ID, parent_tool_use_id, agent name/type. The SDK doesn't inject any agent identity into the raw API request.

## Potential Improvements

### Option A: Conversation Continuity Tracking
- Track a fingerprint of the first user message per context
- Main agent's first message is the session prompt; subagent's first message is the delegated task
- When a new conversation appears (message_count=1 with a new first-message hash), it's a new agent context
- **Pro**: Doesn't rely on tools or system prompt stability
- **Con**: First user message could theoretically collide; need to handle compaction (which also resets message count)

### Option B: Temporal/Nesting Detection
- Track that the main agent is "mid-turn" (sent a request, hasn't received final response)
- Any new conversation that starts during a main agent turn must be a subagent
- **Pro**: Structurally correct — subagents are always nested within main agent turns
- **Con**: Requires tracking request/response pairing; streaming makes this tricky; concurrent subagents add complexity

### Option C: Inject Agent Identity via SDK
- Modify the `ClaudeAgentOptions` or use environment variables to inject a custom header or metadata field identifying the agent
- e.g., set `metadata.agent_context = "main"` or `metadata.agent_context = "subagent:explorer"`
- **Pro**: Definitive identification, no heuristics needed
- **Con**: Requires SDK support (may not be available); couples proxy to SDK internals

### Option D: Cross-Reference with ATIF Adapter
- The ATIF adapter (`atif_adapter.py`) already knows subagent identities via `_register_subagent()` — it tracks `tool_use_id` and agent name from the Agent tool call
- After the session, correlate proxy captures with ATIF adapter's subagent registry by timestamp or request index
- **Pro**: Uses ground truth from the SDK message stream
- **Con**: Only works post-hoc (can't classify in real-time during capture); adds coupling between proxy and adapter

### Option E: Combined Heuristics (Pragmatic)
- Use `tools_hash` as primary signal (current approach)
- Add fallback: if `tools_hash` matches main but `system_prompt` content is structurally different (e.g., contains subagent-specific prompt text), classify as subagent
- Track `message_count` patterns: a sudden drop to 1 with a different system prompt = new subagent, not compaction
- **Pro**: Incrementally better without architectural changes
- **Con**: Still heuristic-based; edge cases remain

## Recommendation

**Short term**: Option E — layer additional heuristics on top of `tools_hash`. Specifically:
1. Keep `tools_hash` as primary classifier
2. Add: if tools_hash matches main BUT message_count == 1 AND main agent's message_count > 1 AND system_prompt_hash differs → classify as subagent with inherited tools
3. Log ambiguous classifications for manual review

**Medium term**: Option D — post-hoc correlation between proxy captures and ATIF adapter's subagent registry. This gives ground truth for analysis even if real-time classification is imperfect.

**Long term**: Option C — advocate for SDK-level agent identity in API requests. This is the only truly robust solution.
