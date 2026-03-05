<script lang="ts">
	import type { StepItem } from "./ChatView.svelte";
	import ThinkingBlock from "./ThinkingBlock.svelte";
	import ToolCallBlock from "./ToolCallBlock.svelte";
	import { renderMarkdown } from "$lib/utils/markdown";

	let {
		items,
		stepIds,
		runName = "",
		sessionIndex = 0,
	}: {
		items: StepItem[];
		stepIds: number[];
		runName?: string;
		sessionIndex?: number;
	} = $props();

	let stepRange = $derived(
		stepIds.length === 1
			? `Step ${stepIds[0]}`
			: `Steps ${stepIds[0]}\u2013${stepIds[stepIds.length - 1]}`
	);
</script>

<div class="max-w-4xl">
	<div class="rounded-lg border border-border bg-card px-4 py-3 space-y-3">
		{#each items as item}
			{#if item.kind === "thinking"}
				<ThinkingBlock content={item.content} />
			{:else if item.kind === "text"}
				{@const html = renderMarkdown(item.content)}
				<div class="text-sm prose prose-sm dark:prose-invert max-w-none prose-p:my-1.5 prose-headings:my-2 prose-ul:my-1.5 prose-ol:my-1.5 prose-li:my-0.5 prose-pre:my-2 prose-pre:bg-muted prose-pre:text-xs prose-code:text-xs prose-code:before:content-none prose-code:after:content-none">
					{@html html}
				</div>
			{:else if item.kind === "tool"}
				<ToolCallBlock call={item.call} result={item.result} {runName} {sessionIndex} />
			{/if}
		{/each}
	</div>
	<div class="text-[11px] text-muted-foreground/60 mt-1 ml-1">{stepRange}</div>
</div>
