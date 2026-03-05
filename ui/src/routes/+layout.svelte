<script lang="ts">
	import "../app.css";

	let { children } = $props();
	let dark = $state(false);

	function toggleDark() {
		dark = !dark;
		document.documentElement.classList.toggle("dark", dark);
	}
</script>

<svelte:head>
	<title>Trajectory Explorer</title>
</svelte:head>

<div class="min-h-screen bg-background text-foreground">
	<header class="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/80">
		<div class="max-w-7xl mx-auto px-6 h-12 flex items-center gap-4">
			<a href="/" class="text-sm font-semibold tracking-tight hover:text-foreground/80 transition-colors">Trajectory Explorer</a>
			<div class="flex-1"></div>
			<button
				onclick={toggleDark}
				class="text-xs px-2.5 py-1 rounded-md bg-secondary text-secondary-foreground hover:bg-accent transition-colors"
			>
				{dark ? "Light" : "Dark"}
			</button>
		</div>
	</header>
	<main class="max-w-7xl mx-auto px-6 py-10">
		{@render children()}
	</main>
</div>
