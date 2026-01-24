<script lang="ts">
  import type { RegionSentiment, RegionConfig } from "$lib/types";
  import { Card } from "$lib/components/ui/card";
  import { Progress } from "$lib/components/ui/progress";

  interface Props {
    region: RegionSentiment | null;
    config: RegionConfig;
    isSelected?: boolean;
    onclick?: () => void;
  }

  let { region, config, isSelected = false, onclick }: Props = $props();

  const sentimentColors = {
    positive: "text-emerald-400",
    neutral: "text-amber-400",
    negative: "text-rose-400",
  };

  const progressColors = {
    positive: "[&>div]:bg-emerald-500",
    neutral: "[&>div]:bg-amber-500",
    negative: "[&>div]:bg-rose-500",
  };
</script>

<button {onclick} class="w-full text-left transition-all duration-200">
  <Card
    class="p-5 bg-slate-800/50 border-slate-700/50 hover:bg-slate-700/50 hover:border-slate-600 transition-all cursor-pointer {isSelected
      ? 'ring-2 ring-blue-500 border-blue-500'
      : ''}"
  >
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center gap-3">
        <span class="text-2xl">{config.emoji}</span>
        <div>
          <h3 class="font-semibold text-slate-100">{config.name}</h3>
          <p class="text-xs text-slate-400">{config.description}</p>
        </div>
      </div>
    </div>

    {#if region}
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span
            class="text-2xl font-bold {sentimentColors[region.sentiment_label]}"
          >
            {region.sentiment_score.toFixed(0)}%
          </span>
          <span
            class="text-xs uppercase tracking-wider font-medium {sentimentColors[
              region.sentiment_label
            ]}"
          >
            {region.sentiment_label}
          </span>
        </div>
        <Progress
          value={region.sentiment_score}
          class="h-2 bg-slate-700 {progressColors[region.sentiment_label]}"
        />
        <p class="text-xs text-slate-500 mt-2">
          {region.headline_count} headlines analyzed
        </p>
      </div>
    {:else}
      <div class="space-y-2">
        <div class="h-8 bg-slate-700/50 rounded animate-pulse"></div>
        <div class="h-2 bg-slate-700/50 rounded animate-pulse"></div>
      </div>
    {/if}
  </Card>
</button>
