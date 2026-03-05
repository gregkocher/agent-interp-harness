<script lang="ts">
	let { text, isFirst = false, stepId = 0 }: {
		text: string;
		isFirst?: boolean;
		stepId?: number;
	} = $props();
</script>

<div class="flex justify-end">
	<div class="max-w-2xl">
		{#if isFirst}
			<div class="text-[11px] text-muted-foreground/60 mb-1 text-right">Session Prompt</div>
		{/if}
		<div class="bg-primary text-primary-foreground rounded-lg px-4 py-3 text-sm">
			<pre class="whitespace-pre-wrap font-sans leading-relaxed">{text}</pre>
		</div>
		<div class="text-[11px] text-muted-foreground/60 mt-1 text-right">Step {stepId}</div>
	</div>
</div>
