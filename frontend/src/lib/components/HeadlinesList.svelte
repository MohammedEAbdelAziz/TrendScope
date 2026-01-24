<script lang="ts">
  import type { Headline } from "$lib/types";
  import { Badge } from "$lib/components/ui/badge";
  import { Separator } from "$lib/components/ui/separator";

  interface Props {
    headlines: Headline[];
    maxItems?: number;
  }

  let { headlines, maxItems = 5 }: Props = $props();

  const displayHeadlines = $derived(headlines.slice(0, maxItems));

  const sentimentColors = {
    positive: "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30",
    neutral: "bg-amber-500/20 text-amber-400 hover:bg-amber-500/30",
    negative: "bg-rose-500/20 text-rose-400 hover:bg-rose-500/30",
  };

  function formatDate(dateString: string | null): string {
    if (!dateString) return "";
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "";
    }
  }
</script>

<div class="space-y-3">
  {#each displayHeadlines as headline, i}
    <a
      href={headline.url}
      target="_blank"
      rel="noopener noreferrer"
      class="block p-4 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-all duration-200 border border-slate-700/50 hover:border-slate-600 group"
    >
      <div class="flex items-start justify-between gap-3">
        <div class="flex-1 min-w-0">
          <h4
            class="font-medium text-slate-100 group-hover:text-white transition-colors line-clamp-2"
          >
            {headline.title}
          </h4>
          <div class="flex items-center gap-2 mt-2 text-sm text-slate-400">
            <span class="font-medium">{headline.source}</span>
            {#if headline.published_at}
              <span>•</span>
              <span>{formatDate(headline.published_at)}</span>
            {/if}
          </div>
        </div>
        <Badge
          class="{sentimentColors[headline.sentiment_label]} flex-shrink-0"
        >
          {headline.sentiment_label}
        </Badge>
      </div>
    </a>
    {#if i < displayHeadlines.length - 1}
      <Separator class="bg-slate-700/30" />
    {/if}
  {/each}

  {#if headlines.length === 0}
    <div class="text-center py-8 text-slate-400">
      <p>No headlines available</p>
    </div>
  {/if}
</div>
