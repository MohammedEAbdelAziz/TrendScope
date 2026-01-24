<script lang="ts">
  import { onMount } from "svelte";
  import {
    fetchAllRegions,
    fetchTrend,
    fetchInsights,
    triggerCollection,
    type TrendDataPoint,
    type InsightItem,
  } from "$lib/api";
  import {
    REGION_CONFIGS,
    type RegionSentiment,
    type SentimentLabel,
  } from "$lib/types";
  import { Card } from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
  import { Badge } from "$lib/components/ui/badge";
  import { Separator } from "$lib/components/ui/separator";

  // Lucide icons
  import {
    Globe2,
    Building2,
    Landmark,
    Map,
    Pyramid,
    Building,
    MapPin,
    TrendingUp,
    TrendingDown,
    Minus,
    RefreshCw,
    Activity,
    BarChart3,
    Lightbulb,
    ArrowUpCircle,
    ArrowDownCircle,
    Circle,
    ChevronUp,
    ChevronDown,
    FileText,
    ExternalLink,
    Clock,
  } from "lucide-svelte";

  // Icon map for regions
  const iconComponents: Record<string, any> = {
    Globe2,
    Building2,
    Landmark,
    Map,
    Pyramid,
    Building,
    MapPin,
  };

  // State
  let regions = $state<RegionSentiment[]>([]);
  let selectedRegionId = $state<string>("global");
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let lastUpdated = $state<Date>(new Date());

  // Trend and Insights data
  let trendData = $state<TrendDataPoint[]>([]);
  let trendDirection = $state<"rising" | "falling" | "stable">("stable");
  let trendChange = $state<number>(0);
  let insights = $state<InsightItem[]>([]);
  let loadingTrend = $state(false);
  let loadingInsights = $state(false);

  // Derived
  const selectedRegion = $derived(
    regions.find((r) => r.region_id === selectedRegionId),
  );
  const selectedConfig = $derived(
    REGION_CONFIGS.find((r) => r.id === selectedRegionId),
  );

  // Sort headlines: Positive and Negative first (signal headlines), then Neutral
  const sortedHeadlines = $derived(() => {
    if (!selectedRegion) return [];
    return [...selectedRegion.top_headlines].sort((a, b) => {
      // Neutral goes to the end (order 1), positive/negative stay at top (order 0)
      const order: Record<SentimentLabel, number> = {
        positive: 0,
        negative: 0,
        neutral: 1,
      };
      return order[a.sentiment_label] - order[b.sentiment_label];
    });
  });

  // Sentiment colors
  const sentimentColors: Record<
    SentimentLabel,
    { text: string; bg: string; progress: string; ring: string }
  > = {
    positive: {
      text: "text-emerald-400",
      bg: "bg-emerald-500/20",
      progress: "bg-emerald-500",
      ring: "stroke-emerald-500",
    },
    neutral: {
      text: "text-amber-400",
      bg: "bg-amber-500/20",
      progress: "bg-amber-500",
      ring: "stroke-amber-500",
    },
    negative: {
      text: "text-rose-400",
      bg: "bg-rose-500/20",
      progress: "bg-rose-500",
      ring: "stroke-rose-500",
    },
  };

  const insightColorMap: Record<string, string> = {
    emerald: "border-emerald-500",
    rose: "border-rose-500",
    amber: "border-amber-500",
    blue: "border-blue-500",
    purple: "border-purple-500",
    cyan: "border-cyan-500",
    indigo: "border-indigo-500",
    slate: "border-slate-500",
  };

  onMount(async () => {
    await loadData();
  });

  async function loadData() {
    isLoading = true;
    error = null;
    try {
      regions = await fetchAllRegions();
      lastUpdated = new Date();
      await loadRegionDetails(selectedRegionId);
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load data";
    } finally {
      isLoading = false;
    }
  }

  async function loadRegionDetails(regionId: string) {
    loadingTrend = true;
    try {
      const trendResponse = await fetchTrend(regionId, 24);
      trendData = trendResponse.data;
      trendDirection = trendResponse.trend;
      trendChange = trendResponse.change;
    } catch (err) {
      console.error("Failed to load trend:", err);
      trendData = [];
    } finally {
      loadingTrend = false;
    }

    loadingInsights = true;
    try {
      const insightsResponse = await fetchInsights(regionId);
      insights = insightsResponse.insights;
    } catch (err) {
      console.error("Failed to load insights:", err);
      insights = [];
    } finally {
      loadingInsights = false;
    }
  }

  async function selectRegion(regionId: string) {
    selectedRegionId = regionId;
    await loadRegionDetails(regionId);
  }

  async function handleRefresh() {
    await triggerCollection();
    await loadData();
  }

  // Professional terminology
  function getSentimentLabel(label: SentimentLabel): string {
    if (label === "positive") return "Optimistic";
    if (label === "negative") return "Pessimistic";
    return "Neutral";
  }
</script>

<svelte:head>
  <title>Enterprise Sentiment Monitor | Global Economic Intelligence</title>
</svelte:head>

<div class="min-h-screen bg-[#0a0f1a]">
  <!-- Header -->
  <header
    class="border-b border-slate-800 bg-[#0d1320] px-4 md:px-6 py-3 md:py-4"
  >
    <div
      class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 max-w-[1600px] mx-auto"
    >
      <div class="flex items-center gap-3">
        <div
          class="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0"
        >
          <BarChart3 class="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 class="text-base md:text-lg font-semibold text-white">
            Enterprise Sentiment Monitor
          </h1>
          <p class="text-xs text-slate-400 hidden sm:block">
            Global Economic Intelligence
          </p>
        </div>
      </div>
      <div class="flex items-center gap-3 md:gap-6 flex-wrap">
        <div class="flex items-center gap-2">
          <Activity class="w-4 h-4 text-emerald-500 animate-pulse" />
          <span class="text-xs md:text-sm text-slate-400 hidden sm:inline"
            >System Operational</span
          >
        </div>
        <div class="flex items-center gap-2 text-xs md:text-sm text-slate-400">
          <Clock class="w-4 h-4" />
          <span class="hidden sm:inline">Last Updated: </span>
          <span class="text-amber-400 font-medium"
            >{lastUpdated.toLocaleTimeString("en-US", {
              hour: "2-digit",
              minute: "2-digit",
              timeZoneName: "short",
            })}</span
          >
        </div>
        <Button
          variant="outline"
          size="sm"
          onclick={handleRefresh}
          disabled={isLoading}
          class="border-slate-700 bg-slate-800 hover:bg-slate-700 text-white"
        >
          <RefreshCw class="w-4 h-4 md:mr-2" />
          <span class="hidden md:inline">Refresh</span>
        </Button>
      </div>
    </div>
  </header>

  <main class="max-w-[1600px] mx-auto p-4 md:p-6">
    {#if error}
      <Card class="p-6 md:p-8 bg-rose-950/30 border-rose-800/50 text-center">
        <h2 class="text-lg md:text-xl font-semibold text-rose-400">
          Connection Error
        </h2>
        <p class="text-slate-400 mt-2 text-sm md:text-base">{error}</p>
        <Button onclick={loadData} class="mt-4">Try Again</Button>
      </Card>
    {:else}
      <div class="flex flex-col lg:grid lg:grid-cols-12 gap-4 md:gap-6">
        <!-- Region Selector - Horizontal scroll on mobile, sidebar on desktop -->
        <div class="lg:col-span-3 order-1 lg:order-none">
          <h2
            class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 md:mb-4"
          >
            Select Region
          </h2>

          <!-- Mobile: Horizontal scroller with compact cards -->
          <div
            class="flex lg:hidden gap-3 overflow-x-auto pb-3 -mx-4 px-4 snap-x snap-mandatory"
            style="-webkit-overflow-scrolling: touch;"
          >
            {#each REGION_CONFIGS as config}
              {@const region = regions.find((r) => r.region_id === config.id)}
              {@const colors = region
                ? sentimentColors[region.sentiment_label]
                : sentimentColors.neutral}
              {@const isSelected = selectedRegionId === config.id}
              {@const IconComponent = iconComponents[config.icon]}

              <button
                onclick={() => selectRegion(config.id)}
                class="flex-shrink-0 w-36 text-left p-3 rounded-lg border transition-all duration-200 snap-start
                  {isSelected
                  ? 'bg-slate-800/80 border-blue-500'
                  : 'bg-slate-900/50 border-slate-800'}"
              >
                <div class="flex items-center gap-2 mb-2">
                  <div
                    class="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0"
                  >
                    <IconComponent class="w-3.5 h-3.5 text-slate-300" />
                  </div>
                  <h3 class="font-semibold text-white text-xs truncate">
                    {config.name}
                  </h3>
                </div>

                {#if region}
                  <div class="flex items-center justify-between">
                    <span class="text-lg font-bold {colors.text}"
                      >{region.sentiment_score.toFixed(0)}%</span
                    >
                    {#if isSelected}
                      <Circle class="w-2 h-2 text-amber-500 fill-amber-500" />
                    {/if}
                  </div>
                {:else if isLoading}
                  <div class="animate-pulse">
                    <div class="h-6 bg-slate-800 rounded w-16"></div>
                  </div>
                {/if}
              </button>
            {/each}
          </div>

          <!-- Desktop: Vertical sidebar cards -->
          <div class="hidden lg:flex lg:flex-col space-y-3">
            {#each REGION_CONFIGS as config}
              {@const region = regions.find((r) => r.region_id === config.id)}
              {@const colors = region
                ? sentimentColors[region.sentiment_label]
                : sentimentColors.neutral}
              {@const isSelected = selectedRegionId === config.id}
              {@const IconComponent = iconComponents[config.icon]}

              <button
                onclick={() => selectRegion(config.id)}
                class="w-full text-left p-4 rounded-lg border transition-all duration-200
                  {isSelected
                  ? 'bg-slate-800/80 border-blue-500'
                  : 'bg-slate-900/50 border-slate-800 hover:bg-slate-800/50 hover:border-slate-700'}"
              >
                <div class="flex items-center gap-3 mb-3">
                  <div
                    class="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center"
                  >
                    <IconComponent class="w-4 h-4 text-slate-300" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="font-semibold text-white text-sm">
                      {config.name}
                    </h3>
                    <p class="text-xs text-slate-500 truncate">
                      {config.description}
                    </p>
                  </div>
                  {#if isSelected}
                    <Circle class="w-2 h-2 text-amber-500 fill-amber-500" />
                  {/if}
                </div>

                {#if region}
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-2xl font-bold {colors.text}"
                      >{region.sentiment_score.toFixed(0)}%</span
                    >
                    <Badge class="{colors.bg} {colors.text} uppercase text-xs"
                      >{getSentimentLabel(region.sentiment_label)}</Badge
                    >
                  </div>

                  <!-- Optimistic vs Pessimistic Bar -->
                  <div
                    class="h-2 rounded-full bg-slate-800 overflow-hidden flex"
                  >
                    {#if region.bull_count + region.bear_count > 0}
                      <div
                        class="h-full bg-emerald-500 transition-all duration-500"
                        style="width: {(region.bull_count /
                          (region.bull_count + region.bear_count)) *
                          100}%"
                      ></div>
                      <div
                        class="h-full bg-rose-500 transition-all duration-500"
                        style="width: {(region.bear_count /
                          (region.bull_count + region.bear_count)) *
                          100}%"
                      ></div>
                    {:else}
                      <div class="h-full bg-amber-500 w-full"></div>
                    {/if}
                  </div>

                  <div class="flex items-center justify-between mt-2">
                    <span class="text-xs text-slate-500"
                      >{region.headline_count} headlines</span
                    >
                    <span class="text-xs text-slate-500">
                      <span class="text-emerald-400"
                        >{region.bull_count} opt.</span
                      >
                      <span class="mx-1">|</span>
                      <span class="text-rose-400">{region.bear_count} pes.</span
                      >
                    </span>
                  </div>
                {:else if isLoading}
                  <div class="animate-pulse space-y-2">
                    <div class="h-8 bg-slate-800 rounded"></div>
                    <div class="h-2 bg-slate-800 rounded"></div>
                  </div>
                {/if}
              </button>
            {/each}
          </div>
        </div>

        <!-- Center Content -->
        <div class="lg:col-span-6 space-y-4 md:space-y-6 order-2 lg:order-none">
          {#if selectedRegion && selectedConfig}
            {@const SelectedIcon = iconComponents[selectedConfig.icon]}

            <!-- Title Section -->
            <div class="flex items-center gap-3 md:gap-4">
              <div
                class="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-slate-800 flex items-center justify-center flex-shrink-0"
              >
                <SelectedIcon class="w-5 h-5 md:w-6 md:h-6 text-blue-400" />
              </div>
              <div>
                <h2 class="text-lg md:text-2xl font-bold text-white">
                  {selectedConfig.name} Sentiment Analysis
                </h2>
                <p class="text-slate-400 text-xs md:text-sm hidden sm:block">
                  Real-time AI analysis of economic news, market reports, and
                  trade policies.
                </p>
                <p class="text-slate-500 text-xs">
                  {selectedRegion.filtered_count > 0
                    ? `${selectedRegion.filtered_count} noise headlines filtered out`
                    : "Noise filter active"}
                </p>
              </div>
            </div>

            <!-- Sentiment Overview Card -->
            <Card class="p-4 md:p-6 bg-slate-900/50 border-slate-800">
              <div
                class="flex flex-col md:flex-row md:items-start md:justify-between gap-4 md:gap-0"
              >
                <!-- Donut Chart + Stats -->
                <div class="flex items-center gap-4 md:gap-8">
                  <div class="relative w-28 h-28 md:w-48 md:h-48 flex-shrink-0">
                    <svg viewBox="0 0 100 100" class="w-full h-full -rotate-90">
                      <circle
                        cx="50"
                        cy="50"
                        r="42"
                        fill="none"
                        stroke="#1e293b"
                        stroke-width="10"
                      />
                      <circle
                        cx="50"
                        cy="50"
                        r="42"
                        fill="none"
                        stroke-width="10"
                        stroke-linecap="round"
                        class={sentimentColors[selectedRegion.sentiment_label]
                          .ring}
                        stroke-dasharray="{(selectedRegion.sentiment_score /
                          100) *
                          264} 264"
                      />
                    </svg>
                    <div
                      class="absolute inset-0 flex flex-col items-center justify-center"
                    >
                      <span class="text-2xl md:text-4xl font-bold text-white"
                        >{selectedRegion.sentiment_score.toFixed(0)}%</span
                      >
                      <span
                        class="text-xs md:text-sm font-medium uppercase tracking-wider {sentimentColors[
                          selectedRegion.sentiment_label
                        ].text}"
                      >
                        {getSentimentLabel(selectedRegion.sentiment_label)}
                      </span>
                    </div>
                  </div>

                  <!-- Stats -->
                  <div class="flex md:flex-col gap-4 md:space-y-4">
                    <div>
                      <p
                        class="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1"
                      >
                        <TrendingUp class="w-3 h-3" />
                        <span class="hidden sm:inline">Optimistic</span><span
                          class="sm:hidden">Opt</span
                        >
                      </p>
                      <p class="text-xl md:text-3xl font-bold text-emerald-400">
                        {selectedRegion.bull_count}
                      </p>
                    </div>
                    <div>
                      <p
                        class="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1"
                      >
                        <TrendingDown class="w-3 h-3" />
                        <span class="hidden sm:inline">Pessimistic</span><span
                          class="sm:hidden">Pes</span
                        >
                      </p>
                      <p class="text-xl md:text-3xl font-bold text-rose-400">
                        {selectedRegion.bear_count}
                      </p>
                    </div>
                    <div class="hidden md:block">
                      <p
                        class="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1"
                      >
                        <Minus class="w-3 h-3" /> Neutral
                      </p>
                      <p class="text-lg font-semibold text-slate-400">
                        {selectedRegion.neutral_count}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Sentiment Balance Visualization -->
                <div class="flex-1 md:ml-8">
                  <p
                    class="text-xs text-slate-500 uppercase tracking-wider mb-3"
                  >
                    Sentiment Balance
                  </p>
                  <div
                    class="h-10 rounded-lg bg-slate-800 overflow-hidden flex relative"
                  >
                    {#if selectedRegion.bull_count + selectedRegion.bear_count > 0}
                      <div
                        class="h-full bg-gradient-to-r from-emerald-600 to-emerald-500 flex items-center justify-center transition-all duration-500"
                        style="width: {(selectedRegion.bull_count /
                          (selectedRegion.bull_count +
                            selectedRegion.bear_count)) *
                          100}%"
                      >
                        <span
                          class="text-white text-sm font-bold flex items-center gap-1"
                        >
                          <ArrowUpCircle class="w-4 h-4" />
                          {selectedRegion.bull_count}
                        </span>
                      </div>
                      <div
                        class="h-full bg-gradient-to-r from-rose-500 to-rose-600 flex items-center justify-center transition-all duration-500"
                        style="width: {(selectedRegion.bear_count /
                          (selectedRegion.bull_count +
                            selectedRegion.bear_count)) *
                          100}%"
                      >
                        <span
                          class="text-white text-sm font-bold flex items-center gap-1"
                        >
                          {selectedRegion.bear_count}
                          <ArrowDownCircle class="w-4 h-4" />
                        </span>
                      </div>
                    {:else}
                      <div
                        class="h-full bg-amber-500/50 w-full flex items-center justify-center"
                      >
                        <span class="text-white text-sm font-bold"
                          >No Active Signals</span
                        >
                      </div>
                    {/if}
                  </div>

                  <div class="flex justify-between mt-2 text-xs text-slate-500">
                    <span>Optimistic</span>
                    <span class="flex items-center gap-1">
                      Trend:
                      {#if trendDirection === "rising"}
                        <ChevronUp class="w-4 h-4 text-emerald-400" />
                        <span class="text-emerald-400">Rising</span>
                      {:else if trendDirection === "falling"}
                        <ChevronDown class="w-4 h-4 text-rose-400" />
                        <span class="text-rose-400">Falling</span>
                      {:else}
                        <Minus class="w-4 h-4 text-slate-400" />
                        <span class="text-slate-400">Stable</span>
                      {/if}
                    </span>
                    <span>Pessimistic</span>
                  </div>
                </div>
              </div>

              <!-- 24h Trend Chart -->
              <div class="mt-6 pt-6 border-t border-slate-800">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-sm font-medium text-slate-300">
                    24h Sentiment Trend
                  </h3>
                  <span class="text-xs text-slate-500">
                    {trendData.length > 0
                      ? `${trendData.length} data points`
                      : "Last 24 Hours"}
                  </span>
                </div>

                {#if loadingTrend}
                  <div
                    class="h-20 bg-slate-800/30 rounded-lg animate-pulse"
                  ></div>
                {:else if trendData.length > 0}
                  <div
                    class="h-24 bg-slate-800/30 rounded-lg flex items-end px-2 pb-2 gap-0.5 relative"
                  >
                    <div
                      class="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-xs text-slate-600 py-1"
                    >
                      <span>100</span>
                      <span>50</span>
                      <span>0</span>
                    </div>
                    <div class="flex-1 flex items-end gap-0.5 ml-6">
                      {#each trendData as point, i}
                        {@const colors =
                          sentimentColors[point.label as SentimentLabel] ||
                          sentimentColors.neutral}
                        <div
                          class="flex-1 rounded-t transition-all duration-300 {colors.progress} hover:opacity-100 cursor-pointer group relative"
                          style="height: {point.score}%; opacity: 0.7"
                          title="{point.score.toFixed(1)}% - {new Date(
                            point.timestamp,
                          ).toLocaleTimeString()}"
                        >
                          <div
                            class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10"
                          >
                            <div
                              class="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs whitespace-nowrap"
                            >
                              <div class="text-white font-medium">
                                {point.score.toFixed(1)}%
                              </div>
                              <div class="text-slate-400">
                                {new Date(point.timestamp).toLocaleTimeString()}
                              </div>
                            </div>
                          </div>
                        </div>
                      {/each}
                    </div>
                  </div>
                {:else}
                  <div
                    class="h-20 bg-slate-800/30 rounded-lg flex items-center justify-center"
                  >
                    <p class="text-slate-500 text-sm">
                      No historical data yet. Data is collected hourly.
                    </p>
                  </div>
                {/if}
              </div>
            </Card>

            <!-- Headlines Section -->
            <Card class="p-4 md:p-6 bg-slate-900/50 border-slate-800">
              <div class="flex items-center gap-2 mb-3 md:mb-4">
                <FileText class="w-4 h-4 md:w-5 md:h-5 text-slate-400" />
                <h3 class="text-base md:text-lg font-semibold text-white">
                  Top Headlines
                </h3>
              </div>

              <div class="space-y-2 md:space-y-3">
                {#each sortedHeadlines().slice(0, 6) as headline}
                  {@const colors = sentimentColors[headline.sentiment_label]}
                  <a
                    href={headline.url}
                    target="_blank"
                    class="block p-3 md:p-4 rounded-lg bg-slate-800/30 hover:bg-slate-800/50 border border-slate-800 hover:border-slate-700 transition-all"
                  >
                    <div class="flex items-start gap-2 md:gap-3">
                      <!-- Sentiment Icon -->
                      <div class="mt-0.5 md:mt-1 flex-shrink-0">
                        {#if headline.sentiment_label === "positive"}
                          <ArrowUpCircle
                            class="w-4 h-4 md:w-5 md:h-5 text-emerald-500"
                          />
                        {:else if headline.sentiment_label === "negative"}
                          <ArrowDownCircle
                            class="w-4 h-4 md:w-5 md:h-5 text-rose-500"
                          />
                        {:else}
                          <Minus class="w-4 h-4 md:w-5 md:h-5 text-amber-500" />
                        {/if}
                      </div>

                      <div class="flex-1 min-w-0">
                        <div
                          class="flex flex-wrap items-center gap-1 md:gap-2 text-xs text-slate-500 mb-1"
                        >
                          <span class="font-medium text-slate-400"
                            >{headline.source}</span
                          >
                          <span class="hidden sm:inline">•</span>
                          <span class="hidden sm:inline"
                            >{headline.published_at
                              ? new Date(
                                  headline.published_at,
                                ).toLocaleDateString("en-US", {
                                  month: "short",
                                  day: "numeric",
                                })
                              : "Today"}</span
                          >
                          <span>•</span>
                          <span class={colors.text}>
                            {getSentimentLabel(headline.sentiment_label)}
                          </span>
                        </div>
                        <h4
                          class="text-white text-sm md:text-base font-medium line-clamp-2"
                        >
                          {headline.title}
                        </h4>
                      </div>

                      <ExternalLink class="w-4 h-4 text-slate-600" />
                    </div>
                  </a>
                {/each}
              </div>
            </Card>
          {:else if isLoading}
            <div class="animate-pulse space-y-6">
              <div class="h-12 bg-slate-800 rounded w-2/3"></div>
              <div class="h-64 bg-slate-800 rounded"></div>
              <div class="h-48 bg-slate-800 rounded"></div>
            </div>
          {/if}
        </div>

        <!-- Right Sidebar - AI Insights -->
        <div class="lg:col-span-3 order-3">
          <Card
            class="p-4 md:p-5 bg-slate-900/50 border-slate-800 lg:sticky lg:top-6"
          >
            <div class="flex items-center gap-2 mb-5">
              <div
                class="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center"
              >
                <Lightbulb class="w-4 h-4 text-amber-400" />
              </div>
              <h3 class="text-lg font-semibold text-white">AI Insights</h3>
            </div>

            {#if loadingInsights}
              <div class="space-y-4">
                {#each [1, 2, 3] as _}
                  <div class="animate-pulse">
                    <div class="h-4 bg-slate-800 rounded w-1/3 mb-2"></div>
                    <div class="h-12 bg-slate-800 rounded"></div>
                  </div>
                {/each}
              </div>
            {:else if insights.length > 0}
              <div class="space-y-4">
                {#each insights as insight}
                  <div
                    class="border-l-2 {insightColorMap[insight.color] ||
                      'border-slate-500'} pl-4 py-1"
                  >
                    <h4
                      class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1"
                    >
                      {insight.title}
                    </h4>
                    <p class="text-sm text-slate-300 leading-relaxed">
                      {insight.text}
                    </p>
                  </div>
                {/each}
              </div>
            {:else}
              <div class="space-y-4">
                <div class="border-l-2 border-amber-500 pl-4 py-1">
                  <h4
                    class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1"
                  >
                    ANALYSIS PENDING
                  </h4>
                  <p class="text-sm text-slate-300 leading-relaxed">
                    Collecting data for AI analysis. Insights will appear after
                    more data points are gathered.
                  </p>
                </div>
              </div>
            {/if}

            <Separator class="my-5 bg-slate-800" />

            <Button
              variant="outline"
              class="w-full border-slate-700 text-slate-300 hover:bg-slate-800"
            >
              View Full Report
            </Button>
          </Card>
        </div>
      </div>
    {/if}
  </main>
</div>
