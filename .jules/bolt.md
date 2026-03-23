## 2025-03-24 - Svelte 5 $derived Function Trap
**Learning:** Defining a Svelte 5 `$derived` as an arrow function (e.g., `const myDerived = $derived(() => { ... })`) creates a derived *function*, not a memoized value. When called in a template (`myDerived()`), it executes on every evaluation, destroying array reference stability and causing unnecessary re-renders in `{#each}` blocks.
**Action:** Use `$derived.by(() => { ... })` for block statements to properly memoize the computed value and maintain reference stability.

## 2025-03-24 - Network Waterfall in SvelteKit Component Loading
**Learning:** Awaiting independent fetch calls sequentially in a UI component's load function (`await fetchTrend(); await fetchInsights();`) creates a network waterfall that unnecessarily blocks full UI rendering and doubles loading time.
**Action:** Use `Promise.all()` to parallelize independent data fetching functions.
