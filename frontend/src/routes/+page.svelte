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
  import { type Locale, getTranslation, isRTL, locales } from "$lib/i18n";
  import { Card } from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
  import { Badge } from "$lib/components/ui/badge";

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
    Languages,
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

  // Localization
  let currentLocale = $state<Locale>("en");
  const t = $derived(getTranslation(currentLocale));
  const rtl = $derived(isRTL(currentLocale));

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
    // Check for saved locale preference
    const savedLocale = localStorage.getItem("locale") as Locale | null;
    if (savedLocale && locales.includes(savedLocale)) {
      currentLocale = savedLocale;
    }
    await loadData();
  });

  function toggleLocale() {
    currentLocale = currentLocale === "en" ? "ar" : "en";
    localStorage.setItem("locale", currentLocale);
  }

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

  // Get localized sentiment label
  function getSentimentLabel(label: SentimentLabel): string {
    if (label === "positive") return t.optimistic;
    if (label === "negative") return t.pessimistic;
    return t.neutral;
  }

  // Get localized region name
  function getRegionName(regionId: string): string {
    return t.regions[regionId as keyof typeof t.regions] || regionId;
  }

  // Get localized region description
  function getRegionDescription(regionId: string): string {
    return (
      t.regionDescriptions[regionId as keyof typeof t.regionDescriptions] || ""
    );
  }
</script>

<svelte:head>
  <title>{t.appTitle} | {t.appSubtitle}</title>
</svelte:head>

<div class="min-h-screen bg-[#0a0f1a]" dir={rtl ? "rtl" : "ltr"}>
  <!-- Header -->
  <header class="border-b border-slate-800 bg-[#0d1320] px-6 py-4">
    <div
      class="flex flex-col md:flex-row md:items-center justify-between max-w-[1600px] mx-auto gap-4"
    >
      <div class="flex items-center gap-3">
        <div
          class="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center shrink-0"
        >
          <BarChart3 class="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 class="text-lg font-semibold text-white">
            {t.appTitle}
          </h1>
          <p class="text-xs text-slate-400">{t.appSubtitle}</p>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-4 md:gap-6">
        <!-- Language Switcher -->
        <Button
          variant="ghost"
          size="sm"
          onclick={toggleLocale}
          class="text-slate-400 hover:text-white"
        >
          <Languages class="w-4 h-4 {rtl ? 'ml-2' : 'mr-2'}" />
          {currentLocale === "en" ? "العربية" : "English"}
        </Button>

        <div class="flex items-center gap-2">
          <Activity class="w-4 h-4 text-emerald-500 animate-pulse" />
          <span class="text-sm text-slate-400">{t.systemOperational}</span>
        </div>
        <div class="flex items-center gap-2 text-sm text-slate-400">
          <Clock class="w-4 h-4" />
          <span
            >{t.lastUpdated}:
            <span class="text-amber-400 font-medium"
              >{lastUpdated.toLocaleTimeString(
                currentLocale === "ar" ? "ar-EG" : "en-US",
                {
                  hour: "2-digit",
                  minute: "2-digit",
                },
              )}</span
            ></span
          >
        </div>
        <Button
          variant="outline"
          size="sm"
          onclick={handleRefresh}
          disabled={isLoading}
          class="border-slate-700 bg-slate-800 hover:bg-slate-700 text-white"
        >
          <RefreshCw class="w-4 h-4 {rtl ? 'ml-2' : 'mr-2'}" />
          {t.refresh}
        </Button>
      </div>
    </div>
  </header>

  <main class="max-w-[1600px] mx-auto p-6">
    {#if error}
      <Card class="p-8 bg-rose-950/30 border-rose-800/50 text-center">
        <h2 class="text-xl font-semibold text-rose-400">{t.connectionError}</h2>
        <p class="text-slate-400 mt-2">{error}</p>
        <Button onclick={loadData} class="mt-4">{t.tryAgain}</Button>
      </Card>
    {:else}
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Left Sidebar - Region Cards -->
        <div class="lg:col-span-3 space-y-3 order-2 lg:order-1">
          <h2
            class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4"
          >
            {t.selectRegion}
          </h2>

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
                    {getRegionName(config.id)}
                  </h3>
                  <p class="text-xs text-slate-500 truncate">
                    {getRegionDescription(config.id)}
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
                <div class="h-2 rounded-full bg-slate-800 overflow-hidden flex">
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
                    >{region.headline_count} {t.headlines}</span
                  >
                  <span class="text-xs text-slate-500">
                    <span class="text-emerald-400"
                      >{region.bull_count} {rtl ? "" : "opt."}</span
                    >
                    <span class="mx-1">|</span>
                    <span class="text-rose-400"
                      >{region.bear_count} {rtl ? "" : "pes."}</span
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

        <!-- Center Content -->
        <div class="lg:col-span-6 space-y-6 order-1 lg:order-2">
          {#if selectedRegion && selectedConfig}
            {@const SelectedIcon = iconComponents[selectedConfig.icon]}

            <!-- Title Section -->
            <div class="flex items-center gap-4">
              <div
                class="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center"
              >
                <SelectedIcon class="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h2 class="text-2xl font-bold text-white">
                  {getRegionName(selectedConfig.id)}
                  {t.sentimentAnalysis}
                </h2>
                <p class="text-slate-400 text-sm">
                  {t.realTimeAnalysis}
                </p>
                <p class="text-slate-500 text-xs">
                  {selectedRegion.filtered_count > 0
                    ? `${selectedRegion.filtered_count} ${t.noiseFiltered}`
                    : t.noiseFilterActive}
                </p>
              </div>
            </div>

            <!-- Sentiment Overview Card -->
            <Card class="p-4 md:p-6 bg-slate-900/50 border-slate-800">
              <div
                class="flex flex-col xl:flex-row items-center xl:items-start justify-between gap-8"
              >
                <!-- Donut Chart -->
                <div
                  class="flex flex-col sm:flex-row items-center gap-6 md:gap-8 w-full xl:w-auto"
                >
                  <div class="relative w-40 h-40 md:w-48 md:h-48 shrink-0">
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
                      <span class="text-4xl font-bold text-white"
                        >{selectedRegion.sentiment_score.toFixed(0)}%</span
                      >
                      <span
                        class="text-sm font-medium uppercase tracking-wider {sentimentColors[
                          selectedRegion.sentiment_label
                        ].text}"
                      >
                        {getSentimentLabel(selectedRegion.sentiment_label)}
                      </span>
                    </div>
                  </div>

                  <!-- Stats -->
                  <div
                    class="grid grid-cols-3 sm:flex sm:flex-col gap-4 w-full"
                  >
                    <div>
                      <p
                        class="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1"
                      >
                        <TrendingUp class="w-3 h-3" />
                        {t.optimistic}
                      </p>
                      <p class="text-3xl font-bold text-emerald-400">
                        {selectedRegion.bull_count}
                      </p>
                    </div>
                    <div>
                      <p
                        class="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1"
                      >
                        <TrendingDown class="w-3 h-3" />
                        {t.pessimistic}
                      </p>
                      <p class="text-3xl font-bold text-rose-400">
                        {selectedRegion.bear_count}
                      </p>
                    </div>
                    <div>
                      <p
                        class="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1"
                      >
                        <Minus class="w-3 h-3" />
                        {t.neutral}
                      </p>
                      <p class="text-lg font-semibold text-slate-400">
                        {selectedRegion.neutral_count}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Sentiment Balance Visualization -->
                <div class="w-full xl:flex-1">
                  <p
                    class="text-xs text-slate-500 uppercase tracking-wider mb-3 text-center xl:text-left"
                  >
                    {t.sentimentBalance}
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
                          >{t.noActiveSignals}</span
                        >
                      </div>
                    {/if}
                  </div>

                  <div class="flex justify-between mt-2 text-xs text-slate-500">
                    <span>{t.optimistic}</span>
                    <span class="flex items-center gap-1">
                      {t.trend}:
                      {#if trendDirection === "rising"}
                        <ChevronUp class="w-4 h-4 text-emerald-400" />
                        <span class="text-emerald-400">{t.rising}</span>
                      {:else if trendDirection === "falling"}
                        <ChevronDown class="w-4 h-4 text-rose-400" />
                        <span class="text-rose-400">{t.falling}</span>
                      {:else}
                        <Minus class="w-4 h-4 text-slate-400" />
                        <span class="text-slate-400">{t.stable}</span>
                      {/if}
                    </span>
                    <span>{t.pessimistic}</span>
                  </div>
                </div>
              </div>

              <!-- 24h Trend Chart -->
              <div class="mt-6 pt-6 border-t border-slate-800">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-sm font-medium text-slate-300">
                    {t.sentimentTrend24h}
                  </h3>
                  <span class="text-xs text-slate-500">
                    {trendData.length > 0
                      ? `${trendData.length} ${t.dataPoints}`
                      : t.last24Hours}
                  </span>
                </div>

                {#if loadingTrend}
                  <div
                    class="h-28 bg-slate-800/30 rounded-lg animate-pulse"
                  ></div>
                {:else if trendData.length > 0}
                  <div
                    class="h-32 bg-slate-800/30 rounded-lg p-3 flex flex-col"
                  >
                    <!-- Y-axis and Scrollable Content -->
                    <div class="flex-1 flex overflow-hidden">
                      <!-- Fixed Y-axis -->
                      <div
                        class="flex flex-col justify-between text-[10px] text-slate-500 {rtl
                          ? 'pl-2'
                          : 'pr-2'} pb-1"
                      >
                        <span>100</span>
                        <span>50</span>
                        <span>0</span>
                      </div>

                      <!-- Scrollable Content -->
                      <div
                        class="flex-1 overflow-x-auto overflow-y-hidden custom-scrollbar"
                      >
                        <div
                          class="h-full flex flex-col min-w-full"
                          style="width: {Math.max(
                            100,
                            trendData.length * 20,
                          )}px"
                        >
                          <!-- Bars Row -->
                          <div
                            class="flex-1 flex items-end justify-start px-1 relative"
                          >
                            {#each trendData as point}
                              <div
                                class="h-full flex flex-col justify-end group relative flex-1 min-w-[12px] max-w-[40px]"
                              >
                                <!-- Bar -->
                                <div
                                  class="mx-0.5 rounded-t-sm transition-all duration-300 hover:opacity-90 relative"
                                  style="height: {Math.max(
                                    point.score,
                                    4,
                                  )}%; background-color: {point.label ===
                                  'positive'
                                    ? '#10b981'
                                    : point.label === 'negative'
                                      ? '#f43f5e'
                                      : '#f59e0b'};"
                                >
                                  <!-- Gradient overlay -->
                                  <div
                                    class="absolute inset-0 bg-gradient-to-b from-white/10 to-transparent rounded-t-sm"
                                  ></div>
                                </div>

                                <!-- Tooltip -->
                                <div
                                  class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-20 w-max pointer-events-none transform transition-all duration-200"
                                >
                                  <div
                                    class="bg-slate-900/95 backdrop-blur-sm border border-slate-700 p-2.5 rounded-lg shadow-xl flex flex-col gap-1 min-w-[100px]"
                                  >
                                    <div
                                      class="flex items-center justify-between gap-4"
                                    >
                                      <span
                                        class="text-xs text-slate-400 font-medium"
                                        >Score</span
                                      >
                                      <span
                                        class="text-sm font-bold"
                                        style="color: {point.label ===
                                        'positive'
                                          ? '#34d399'
                                          : point.label === 'negative'
                                            ? '#fb7185'
                                            : '#fbbf24'}"
                                        >{point.score.toFixed(1)}%</span
                                      >
                                    </div>
                                    <div
                                      class="w-full h-1 bg-slate-800 rounded-full overflow-hidden"
                                    >
                                      <div
                                        class="h-full"
                                        style="width: {point.score}%; background-color: {point.label ===
                                        'positive'
                                          ? '#34d399'
                                          : point.label === 'negative'
                                            ? '#fb7185'
                                            : '#fbbf24'}"
                                      ></div>
                                    </div>
                                    <div
                                      class="flex items-center justify-between gap-4 mt-1 pt-1 border-t border-slate-800"
                                    >
                                      <span class="text-[10px] text-slate-500"
                                        >Time</span
                                      >
                                      <span class="text-xs text-slate-300"
                                        >{new Date(
                                          point.timestamp,
                                        ).toLocaleTimeString([], {
                                          hour: "numeric",
                                          minute: "2-digit",
                                        })}</span
                                      >
                                    </div>
                                  </div>
                                  <div
                                    class="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-slate-700"
                                  ></div>
                                </div>
                              </div>
                            {/each}
                          </div>

                          <!-- Labels Row -->
                          <div
                            class="flex items-start justify-start px-1 h-6 mt-1 border-t border-slate-800/30"
                          >
                            {#each trendData as point, i}
                              <div
                                class="flex-1 min-w-[12px] max-w-[40px] flex justify-center"
                              >
                                <span
                                  class="text-[9px] text-slate-500 whitespace-nowrap {i %
                                    Math.ceil(trendData.length / 8) !==
                                  0
                                    ? 'hidden'
                                    : ''}"
                                >
                                  {new Date(point.timestamp).toLocaleTimeString(
                                    [],
                                    {
                                      hour: "numeric",
                                      minute: "2-digit",
                                    },
                                  )}
                                </span>
                              </div>
                            {/each}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                {:else}
                  <div
                    class="h-20 bg-slate-800/30 rounded-lg flex items-center justify-center"
                  >
                    <p class="text-slate-500 text-sm">
                      {t.noHistoricalData}
                    </p>
                  </div>
                {/if}
              </div>
            </Card>

            <!-- Headlines Section -->
            <Card class="p-6 bg-slate-900/50 border-slate-800">
              <div class="flex items-center gap-2 mb-4">
                <FileText class="w-5 h-5 text-slate-400" />
                <h3 class="text-lg font-semibold text-white">
                  {t.topHeadlines}
                </h3>
              </div>

              <div class="space-y-3">
                {#each sortedHeadlines().slice(0, 8) as headline}
                  {@const colors = sentimentColors[headline.sentiment_label]}
                  <a
                    href={headline.url}
                    target="_blank"
                    class="block p-4 rounded-lg bg-slate-800/30 hover:bg-slate-800/50 border border-slate-800 hover:border-slate-700 transition-all"
                  >
                    <div class="flex items-start gap-3">
                      <!-- Sentiment Icon -->
                      <div class="mt-1">
                        {#if headline.sentiment_label === "positive"}
                          <ArrowUpCircle class="w-5 h-5 text-emerald-500" />
                        {:else if headline.sentiment_label === "negative"}
                          <ArrowDownCircle class="w-5 h-5 text-rose-500" />
                        {:else}
                          <Minus class="w-5 h-5 text-amber-500" />
                        {/if}
                      </div>

                      <div class="flex-1">
                        <div
                          class="flex items-center gap-2 text-xs text-slate-500 mb-1"
                        >
                          <span class="font-medium text-slate-400"
                            >{headline.source}</span
                          >
                          <span>•</span>
                          <span
                            >{headline.published_at
                              ? new Date(
                                  headline.published_at,
                                ).toLocaleDateString(
                                  currentLocale === "ar" ? "ar-EG" : "en-US",
                                  {
                                    month: "short",
                                    day: "numeric",
                                  },
                                )
                              : t.today}</span
                          >
                          <span>•</span>
                          <span class={colors.text}>
                            {getSentimentLabel(headline.sentiment_label)}
                          </span>
                        </div>
                        <h4 class="text-white font-medium">{headline.title}</h4>
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
          <Card class="p-5 bg-slate-900/50 border-slate-800 sticky top-6">
            <div class="flex items-center gap-2 mb-5">
              <div
                class="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center"
              >
                <Lightbulb class="w-4 h-4 text-amber-400" />
              </div>
              <h3 class="text-lg font-semibold text-white">{t.insights}</h3>
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
                    class="{rtl
                      ? 'border-r-2 pr-4'
                      : 'border-l-2 pl-4'} {insightColorMap[insight.color] ||
                      'border-slate-500'} py-1"
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
                <div
                  class="{rtl
                    ? 'border-r-2 pr-4'
                    : 'border-l-2 pl-4'} border-amber-500 py-1"
                >
                  <h4
                    class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1"
                  >
                    {t.analysisPending}
                  </h4>
                  <p class="text-sm text-slate-300 leading-relaxed">
                    {t.analysisPendingText}
                  </p>
                </div>
              </div>
            {/if}
          </Card>
        </div>
      </div>
    {/if}
  </main>

  <!-- Footer -->
  <footer class="border-t border-slate-800 bg-[#0d1320] py-12 mt-12">
    <div class="max-w-[1600px] mx-auto px-6 text-center">
      <div class="flex flex-col items-center gap-6">
        <!-- Credits -->
        <div class="flex items-center gap-2 text-slate-300">
          <span>{t.footer.createdBy}</span>
          <a
            href="https://mohammedeabdelaziz.github.io/"
            target="_blank"
            class="text-blue-400 hover:text-blue-300 transition-colors font-medium border-b border-blue-400/30 hover:border-blue-300 pb-0.5"
          >
            Mohammed Essam
          </a>
        </div>

        <!-- Repo Link -->
        <a
          href="https://github.com/MohammedEAbdelAziz/TrendScope"
          target="_blank"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800/50 hover:bg-slate-800 border border-slate-700 hover:border-slate-600 transition-all text-sm text-slate-300 hover:text-white group"
        >
          <svg
            viewBox="0 0 24 24"
            class="w-4 h-4 fill-current transition-transform group-hover:scale-110"
            aria-hidden="true"
          >
            <path
              d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
            />
          </svg>
          {t.footer.repo}
        </a>

        <!-- Disclaimer -->
        <div class="max-w-2xl text-xs text-slate-500 leading-relaxed">
          <p>{t.footer.disclaimer}</p>
        </div>
      </div>
    </div>
  </footer>
</div>
