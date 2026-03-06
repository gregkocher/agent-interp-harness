<script lang="ts">
	interface ContentBlock {
		type: string;
		text?: string;
		thinking?: string;
		name?: string;
		input?: Record<string, unknown>;
		content?: string | ContentBlock[];
	}

	interface Edit {
		path: string;
		original: string;
		replacement: string;
	}

	interface MessageEditorProps {
		messages: { role: string; content: string | ContentBlock[] }[];
		lastN?: number;
		onsubmit: (edits: Edit[], label: string, count: number) => void;
	}

	let { messages, lastN = 6, onsubmit }: MessageEditorProps = $props();

	// Show only the last N messages
	let startIdx = $derived(Math.max(0, messages.length - lastN));
	let visibleMessages = $derived(messages.slice(startIdx));

	// Track edits as we go
	let edits = $state<Edit[]>([]);
	let label = $state("");
	let count = $state(3);

	function getBlockText(block: ContentBlock): string {
		if (block.type === "text") return block.text || "";
		if (block.type === "thinking") return block.thinking || "";
		if (block.type === "tool_result") {
			if (typeof block.content === "string") return block.content;
			if (Array.isArray(block.content)) {
				return block.content
					.filter((b) => b.type === "text")
					.map((b) => b.text || "")
					.join("\n");
			}
			return "";
		}
		return "";
	}

	function handleEdit(msgIdx: number, blockIdx: number, field: string, newValue: string) {
		const absIdx = startIdx + msgIdx;
		const msg = messages[absIdx];
		if (!msg || !Array.isArray(msg.content)) return;

		const block = msg.content[blockIdx] as ContentBlock;
		const original = field === "thinking" ? (block.thinking || "") : (block.text || "");

		if (newValue === original) {
			// Remove edit if reverted
			edits = edits.filter((e) => e.path !== `messages[${absIdx}].content[${blockIdx}].${field}`);
			return;
		}

		const path = `messages[${absIdx}].content[${blockIdx}].${field}`;
		// Replace existing edit for same path or add new
		const existing = edits.findIndex((e) => e.path === path);
		const edit: Edit = { path, original, replacement: newValue };
		if (existing >= 0) {
			edits[existing] = edit;
			edits = [...edits]; // trigger reactivity
		} else {
			edits = [...edits, edit];
		}
	}

	function handleToolResultEdit(msgIdx: number, blockIdx: number, newValue: string) {
		const absIdx = startIdx + msgIdx;
		const msg = messages[absIdx];
		if (!msg || !Array.isArray(msg.content)) return;

		const block = msg.content[blockIdx] as ContentBlock;
		let original = "";
		let field = "content";

		if (typeof block.content === "string") {
			original = block.content;
		} else if (Array.isArray(block.content)) {
			// Find first text block
			const textBlock = block.content.find((b) => b.type === "text");
			if (textBlock) {
				original = textBlock.text || "";
				field = "content[0].text"; // simplified path
			}
		}

		if (newValue === original) {
			edits = edits.filter((e) => !e.path.startsWith(`messages[${absIdx}].content[${blockIdx}]`));
			return;
		}

		const path = `messages[${absIdx}].content[${blockIdx}].${field}`;
		const existing = edits.findIndex((e) => e.path === path);
		const edit: Edit = { path, original, replacement: newValue };
		if (existing >= 0) {
			edits[existing] = edit;
			edits = [...edits];
		} else {
			edits = [...edits, edit];
		}
	}

	function handleSubmit() {
		if (edits.length === 0) return;
		onsubmit(edits, label || `${edits.length} edit${edits.length > 1 ? "s" : ""}`, count);
	}

	function isSystemReminder(block: ContentBlock): boolean {
		return block.type === "text" && (block.text?.trimStart().startsWith("<system-reminder>") ?? false);
	}

	function systemReminderLabel(text: string): string {
		// Extract a short label from the content
		const inner = text.replace(/<\/?system-reminder>/g, "").trim();
		const firstLine = inner.split("\n")[0].trim();
		if (firstLine.length > 60) return firstLine.slice(0, 60) + "...";
		return firstLine || "system-reminder";
	}

	// Track which system-reminder blocks are expanded
	let expandedReminders = $state<Set<string>>(new Set());

	function toggleReminder(key: string) {
		const next = new Set(expandedReminders);
		if (next.has(key)) next.delete(key);
		else next.add(key);
		expandedReminders = next;
	}

	function roleBadgeClass(role: string): string {
		switch (role) {
			case "user":
				return "bg-blue-500/20 text-blue-300";
			case "assistant":
				return "bg-emerald-500/20 text-emerald-300";
			default:
				return "bg-muted text-muted-foreground";
		}
	}
</script>

<div class="space-y-3">
	<div class="text-xs text-muted-foreground mb-2">
		Showing last {visibleMessages.length} of {messages.length} messages. Edit text to create a variant.
	</div>

	{#each visibleMessages as msg, msgIdx}
		<div class="rounded-md border border-border bg-card overflow-hidden">
			<!-- Role header -->
			<div class="px-3 py-1.5 border-b border-border bg-muted/30 flex items-center gap-2">
				<span class="text-[10px] font-medium px-1.5 py-0.5 rounded {roleBadgeClass(msg.role)}">
					{msg.role}
				</span>
				<span class="text-[10px] text-muted-foreground/50 font-mono">
					msg[{startIdx + msgIdx}]
				</span>
			</div>

			<!-- Content blocks -->
			<div class="px-3 py-2 space-y-2">
				{#if typeof msg.content === "string"}
					<pre class="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap">{msg.content}</pre>
				{:else if Array.isArray(msg.content)}
					{#each msg.content as block, blockIdx}
						{#if block.type === "thinking"}
							<div>
								<div class="text-[9px] text-muted-foreground/50 uppercase tracking-wider mb-0.5">thinking</div>
								<textarea
									value={block.thinking || ""}
									oninput={(e) => handleEdit(msgIdx, blockIdx, "thinking", e.currentTarget.value)}
									class="w-full text-[10px] font-mono bg-muted/20 border border-border/50 rounded px-2 py-1.5 text-muted-foreground italic resize-y min-h-[60px]"
									rows="3"
								></textarea>
							</div>
						{:else if isSystemReminder(block)}
							{@const rKey = `${msgIdx}-${blockIdx}`}
							{@const isOpen = expandedReminders.has(rKey)}
							<div class="rounded border border-border/30 bg-muted/10 overflow-hidden">
								<button
									onclick={() => toggleReminder(rKey)}
									class="w-full flex items-center gap-1.5 px-2 py-1 text-left"
								>
									<span class="text-[9px] text-muted-foreground/40 transition-transform {isOpen ? 'rotate-90' : ''}">&rsaquo;</span>
									<span class="text-[9px] text-muted-foreground/40 uppercase tracking-wider">system-reminder</span>
									<span class="text-[9px] text-muted-foreground/30 truncate">{systemReminderLabel(block.text || "")}</span>
								</button>
								{#if isOpen}
									<div class="px-2 pb-1.5">
										<textarea
											value={block.text || ""}
											oninput={(e) => handleEdit(msgIdx, blockIdx, "text", e.currentTarget.value)}
											class="w-full text-[10px] font-mono bg-background border border-border/50 rounded px-2 py-1.5 resize-y min-h-[60px] text-muted-foreground/70"
											rows="4"
										></textarea>
									</div>
								{/if}
							</div>
						{:else if block.type === "text"}
							<div>
								<div class="text-[9px] text-muted-foreground/50 uppercase tracking-wider mb-0.5">text</div>
								<textarea
									value={block.text || ""}
									oninput={(e) => handleEdit(msgIdx, blockIdx, "text", e.currentTarget.value)}
									class="w-full text-[10px] font-mono bg-background border border-border/50 rounded px-2 py-1.5 resize-y min-h-[40px]"
									rows="2"
								></textarea>
							</div>
						{:else if block.type === "tool_use"}
							<div class="rounded bg-muted/20 px-2 py-1.5">
								<span class="text-[9px] text-muted-foreground/50 uppercase tracking-wider">tool_use</span>
								<span class="text-[10px] font-mono text-muted-foreground ml-1">{block.name}</span>
							</div>
						{:else if block.type === "tool_result"}
							<div>
								<div class="text-[9px] text-muted-foreground/50 uppercase tracking-wider mb-0.5">tool_result</div>
								<textarea
									value={getBlockText(block)}
									oninput={(e) => handleToolResultEdit(msgIdx, blockIdx, e.currentTarget.value)}
									class="w-full text-[10px] font-mono bg-background border border-border/50 rounded px-2 py-1.5 resize-y min-h-[40px]"
									rows="3"
								></textarea>
							</div>
						{:else}
							<div class="text-[10px] text-muted-foreground/50">
								[{block.type}]
							</div>
						{/if}
					{/each}
				{/if}
			</div>
		</div>
	{/each}

	<!-- Submit bar -->
	<div class="flex items-center gap-3 p-3 rounded-lg border border-border bg-muted/30">
		<label class="text-xs text-muted-foreground">
			Label:
			<input
				type="text"
				bind:value={label}
				placeholder="describe the edit"
				class="ml-1 px-2 py-1 text-xs rounded border border-border bg-background w-48"
			/>
		</label>
		<label class="text-xs text-muted-foreground">
			Count:
			<input
				type="number"
				bind:value={count}
				min="1"
				max="20"
				class="ml-1 w-14 px-2 py-1 text-xs rounded border border-border bg-background"
			/>
		</label>
		<button
			onclick={handleSubmit}
			disabled={edits.length === 0}
			class="px-4 py-1.5 text-xs rounded bg-amber-600 text-white hover:bg-amber-500 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
		>
			Run variant ({edits.length} edit{edits.length > 1 ? "s" : ""})
		</button>
		{#if edits.length > 0}
			<span class="text-[10px] text-amber-400/80">{edits.map((e) => e.path.split(".").pop()).join(", ")}</span>
		{/if}
	</div>
</div>
