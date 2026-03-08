<script lang="ts">
	import type { Step } from "$lib/types/atif";

	let { steps }: { steps: Step[] } = $props();

	const TOOL_EMOJI: Record<string, string> = {
		Read: "📖",
		Write: "✏️",
		Edit: "✏️",
		MultiEdit: "✏️",
		Bash: "💻",
		Glob: "🔍",
		Grep: "🔎",
		Agent: "🤖",
		TodoWrite: "📝",
	};

	type ToolEvent = { kind: "tool"; stepId: number; tool: string; emoji: string };
	type CompactionEvent = { kind: "compaction"; stepId: number };
	type Event = ToolEvent | CompactionEvent;

	let events = $derived.by(() => {
		const result: Event[] = [];
		for (const s of steps) {
			if (
				s.source === "user" &&
				typeof s.message === "string" &&
				s.message.startsWith("This session is being continued")
			) {
				result.push({ kind: "compaction", stepId: s.step_id });
			}
			if (s.tool_calls?.length) {
				for (const tc of s.tool_calls) {
					result.push({
						kind: "tool",
						stepId: s.step_id,
						tool: tc.function_name,
						emoji: TOOL_EMOJI[tc.function_name] ?? "🔧",
					});
				}
			}
		}
		return result;
	});

	let maxStep = $derived(steps.length > 0 ? steps[steps.length - 1].step_id : 0);

	const SVG_HEIGHT = 44;
	const PADDING_LEFT = 8;
	const PADDING_RIGHT = 20;

	let containerEl = $state<HTMLDivElement | null>(null);
	let containerWidth = $state(800);

	$effect(() => {
		if (!containerEl) return;
		const ro = new ResizeObserver((entries) => {
			for (const entry of entries) {
				containerWidth = entry.contentRect.width;
			}
		});
		ro.observe(containerEl);
		return () => ro.disconnect();
	});

	let usableWidth = $derived(Math.max(containerWidth - PADDING_LEFT - PADDING_RIGHT, 100));
	// Only exceed container width if emojis would overlap; otherwise fit exactly
	let svgWidth = $derived(
		events.length * 18 > usableWidth
			? events.length * 18 + PADDING_LEFT + PADDING_RIGHT
			: containerWidth
	);

	function x(stepId: number): number {
		return PADDING_LEFT + (stepId / maxStep) * usableWidth;
	}

	let ticks = $derived.by(() => {
		if (maxStep <= 20) {
			return Array.from({ length: maxStep + 1 }, (_, i) => i).filter((i) => i % 5 === 0 && i > 0);
		}
		const interval = maxStep <= 50 ? 10 : 20;
		const result: number[] = [];
		for (let i = interval; i <= maxStep; i += interval) result.push(i);
		return result;
	});
</script>

{#if events.length > 0}
	<div
		bind:this={containerEl}
		style="border: 1px solid var(--border); border-radius: 0.5rem; background: var(--card); overflow-x: auto; max-width: 100%;"
	>
		<svg width={svgWidth} height={SVG_HEIGHT} style="display: block;">
			<!-- Tick marks -->
			{#each ticks as tick}
				<line
					x1={x(tick)}
					y1={0}
					x2={x(tick)}
					y2={SVG_HEIGHT}
					stroke="var(--border)"
					stroke-width="1"
					opacity="0.5"
				/>
				<text
					x={x(tick) + 3}
					y={SVG_HEIGHT - 4}
					fill="var(--muted-foreground)"
					font-size="9"
					font-family="var(--font-sans)"
				>
					{tick}
				</text>
			{/each}

			<!-- Events -->
			{#each events as event}
				{#if event.kind === "compaction"}
					<line
						x1={x(event.stepId)}
						y1={0}
						x2={x(event.stepId)}
						y2={SVG_HEIGHT}
						stroke="var(--destructive)"
						stroke-width="2"
						stroke-dasharray="4 3"
					/>
					<title>Compaction at step {event.stepId}</title>
				{:else}
					<text
						x={x(event.stepId)}
						y={20}
						font-size="14"
						text-anchor="middle"
						dominant-baseline="central"
						style="cursor: default; user-select: none;"
					>
						{event.emoji}
						<title>{event.tool} (step {event.stepId})</title>
					</text>
				{/if}
			{/each}
		</svg>
	</div>
{/if}
