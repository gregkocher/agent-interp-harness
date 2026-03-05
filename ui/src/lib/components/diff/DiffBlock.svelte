<script lang="ts">
	let { content }: { content: string } = $props();
	let lines = $derived(content.split("\n"));

	function lineClass(line: string): string {
		if (line.startsWith("+") && !line.startsWith("+++")) {
			return "bg-green-600/15 text-green-800 dark:bg-green-500/15 dark:text-green-300 border-l-2 border-green-500/50";
		}
		if (line.startsWith("-") && !line.startsWith("---")) {
			return "bg-red-600/15 text-red-800 dark:bg-red-500/15 dark:text-red-300 border-l-2 border-red-500/50";
		}
		if (line.startsWith("@@")) {
			return "bg-blue-600/10 text-blue-700 dark:bg-blue-500/10 dark:text-blue-300 border-l-2 border-blue-500/40";
		}
		if (line.startsWith("diff ") || line.startsWith("index ") || line.startsWith("---") || line.startsWith("+++")) {
			return "text-muted-foreground bg-muted/30";
		}
		return "text-foreground/70";
	}
</script>

<div class="rounded-lg border border-border overflow-hidden font-mono text-xs">
	{#each lines as line}
		<div class="px-3 py-px leading-5 {lineClass(line)}">
			<pre class="whitespace-pre-wrap">{line}</pre>
		</div>
	{/each}
</div>
