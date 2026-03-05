<script lang="ts">
	import { formatCost, formatDate } from "$lib/utils/format";

	let { data } = $props();
	let search = $state("");

	let filtered = $derived(
		data.runs.filter((r) => {
			if (!search) return true;
			const q = search.toLowerCase();
			return (
				r.run_name.toLowerCase().includes(q) ||
				r.model.toLowerCase().includes(q) ||
				r.tags.some((t: string) => t.toLowerCase().includes(q))
			);
		})
	);
</script>

<div class="space-y-8">
	<div class="flex items-center justify-between">
		<h1 class="text-lg font-semibold">Runs</h1>
		<input
			type="text"
			placeholder="Filter by name, model, or tag..."
			bind:value={search}
			class="h-8 px-3 text-sm rounded-md border border-input bg-background w-64 placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-ring/20 focus:border-ring transition-colors"
		/>
	</div>

	{#if filtered.length === 0}
		<p class="text-muted-foreground text-sm py-12 text-center">
			{data.runs.length === 0 ? "No runs found. Check your RUNS_DIR." : "No runs match your filter."}
		</p>
	{:else}
		<div class="rounded-lg border border-border overflow-hidden">
			<table class="w-full text-sm">
				<thead>
					<tr class="bg-muted/50 border-b border-border text-xs text-muted-foreground">
						<th class="text-left px-4 py-2.5 font-medium">Run</th>
						<th class="text-left px-4 py-2.5 font-medium">Model</th>
						<th class="text-center px-4 py-2.5 font-medium">Sessions</th>
						<th class="text-right px-4 py-2.5 font-medium">Steps</th>
						<th class="text-right px-4 py-2.5 font-medium">Cost</th>
						<th class="text-left px-4 py-2.5 font-medium">Tags</th>
						<th class="text-right px-4 py-2.5 font-medium">Date</th>
					</tr>
				</thead>
				<tbody>
					{#each filtered as run}
						<tr class="border-b border-border last:border-b-0 hover:bg-muted/30 transition-colors">
							<td class="px-4 py-3">
								<a href="/runs/{run.run_name}" class="font-medium text-sm hover:underline underline-offset-4">
									{run.run_name}
								</a>
								{#if run.errors.length > 0}
									<span class="ml-1.5 inline-block w-1.5 h-1.5 rounded-full bg-destructive"></span>
								{/if}
								<div class="flex items-center gap-1.5 mt-0.5">
									<span class="text-xs text-muted-foreground">{run.provider}</span>
									<span class="text-xs text-muted-foreground">&middot;</span>
									<span class="text-xs text-muted-foreground">{run.session_mode}</span>
								</div>
							</td>
							<td class="px-4 py-3 text-muted-foreground font-mono text-xs">{run.model}</td>
							<td class="px-4 py-3 text-center tabular-nums">{run.session_count}</td>
							<td class="px-4 py-3 text-right tabular-nums">{run.total_steps}</td>
							<td class="px-4 py-3 text-right tabular-nums font-mono text-xs">
								{formatCost(run.total_cost_usd)}
							</td>
							<td class="px-4 py-3">
								<div class="flex gap-1 flex-wrap">
									{#each run.tags as tag}
										<span class="px-1.5 py-0.5 rounded-full text-[11px] border border-border text-foreground/70">{tag}</span>
									{/each}
								</div>
							</td>
							<td class="px-4 py-3 text-right text-muted-foreground text-xs whitespace-nowrap tabular-nums">
								{formatDate(run.started_at)}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
