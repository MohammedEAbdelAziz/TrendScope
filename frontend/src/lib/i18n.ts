/**
 * Internationalization (i18n) configuration
 * Supports English and Arabic with professional terminology
 */

export type Locale = "en" | "ar";

export const locales: Locale[] = ["en", "ar"];
export const defaultLocale: Locale = "en";

export interface Translations {
  // Header
  appTitle: string;
  appSubtitle: string;
  systemOperational: string;
  lastUpdated: string;
  refresh: string;

  // Regions
  selectRegion: string;
  headlines: string;
  optimistic: string;
  pessimistic: string;
  neutral: string;

  // Region names
  regions: {
    global: string;
    us: string;
    eu: string;
    africa: string;
    egypt: string;
    saudi: string;
    middleeast: string;
  };

  // Region descriptions
  regionDescriptions: {
    global: string;
    us: string;
    eu: string;
    africa: string;
    egypt: string;
    saudi: string;
    middleeast: string;
  };

  // Sentiment
  sentimentAnalysis: string;
  realTimeAnalysis: string;
  noiseFilterActive: string;
  noiseFiltered: string;
  sentimentBalance: string;
  noActiveSignals: string;
  trend: string;
  rising: string;
  falling: string;
  stable: string;

  // Headlines
  topHeadlines: string;
  today: string;

  // Insights
  insights: string;
  analysisPending: string;
  analysisPendingText: string;

  // Trend chart
  sentimentTrend24h: string;
  dataPoints: string;
  last24Hours: string;
  noHistoricalData: string;

  // Errors
  connectionError: string;
  tryAgain: string;
  // Footer
  footer: {
    createdBy: string;
    repo: string;
    disclaimer: string;
    builtBy: string;
    hireText: string;
  };
}

export const translations: Record<Locale, Translations> = {
  en: {
    appTitle: "TrendScope",
    appSubtitle: "Economic Sentiment at a Glance",
    systemOperational: "System Operational",
    lastUpdated: "Last Updated",
    refresh: "Refresh",

    selectRegion: "Select Region",
    headlines: "headlines",
    optimistic: "Optimistic",
    pessimistic: "Pessimistic",
    neutral: "Neutral",

    regions: {
      global: "Global",
      us: "United States",
      eu: "European Union",
      africa: "Africa",
      egypt: "Egypt",
      saudi: "Saudi Arabia",
      middleeast: "Middle East",
    },

    regionDescriptions: {
      global: "Worldwide Economic News",
      us: "US Markets & Economy",
      eu: "European Markets & Trade",
      africa: "African Development & Trade",
      egypt: "Egyptian Economy",
      saudi: "Saudi Vision 2030 & Economy",
      middleeast: "Regional Economic News",
    },

    sentimentAnalysis: "Sentiment Analysis",
    realTimeAnalysis:
      "Automated analysis of economic news, market reports, and trade policies.",
    noiseFilterActive: "Noise filter active",
    noiseFiltered: "noise headlines filtered out",
    sentimentBalance: "Sentiment Balance",
    noActiveSignals: "No Active Signals",
    trend: "Trend",
    rising: "Rising",
    falling: "Falling",
    stable: "Stable",

    topHeadlines: "Top Headlines Impacting Sentiment",
    today: "Today",

    insights: "Insights",
    analysisPending: "ANALYSIS PENDING",
    analysisPendingText:
      "Collecting data for analysis. Insights will appear after more data points are gathered.",

    sentimentTrend24h: "24h Sentiment Trend",
    dataPoints: "data points",
    last24Hours: "Last 24 Hours",
    noHistoricalData: "No historical data yet. Data is collected hourly.",

    connectionError: "Connection Error",
    tryAgain: "Try Again",

    footer: {
      createdBy: "Created by Mohammed Essam",
      repo: "TrendScope GitHub Repo",
      disclaimer:
        "Traffic Data collection via Umami. I am not liable for data accuracy. This is not trade advice.",
      builtBy: "Built by",
      hireText: "Need custom analytics or data solutions?",
    },
  },

  ar: {
    // Professional Arabic translations - formal business terminology
    appTitle: "مرصد الاقتصاد",
    appSubtitle: "تحليل المعنويات الاقتصادية",
    systemOperational: "النظام يعمل",
    lastUpdated: "آخر تحديث",
    refresh: "تحديث",

    selectRegion: "اختر المنطقة",
    headlines: "عنوان",
    optimistic: "متفائل",
    pessimistic: "متشائم",
    neutral: "محايد",

    regions: {
      global: "العالم",
      us: "الولايات المتحدة",
      eu: "الاتحاد الأوروبي",
      africa: "أفريقيا",
      egypt: "مصر",
      saudi: "السعودية",
      middleeast: "الشرق الأوسط",
    },

    regionDescriptions: {
      global: "الأخبار الاقتصادية العالمية",
      us: "الأسواق والاقتصاد الأمريكي",
      eu: "أسواق وتجارة أوروبا",
      africa: "التنمية والتجارة الأفريقية",
      egypt: "الاقتصاد المصري",
      saudi: "رؤية 2030 والاقتصاد السعودي",
      middleeast: "الأخبار الاقتصادية الإقليمية",
    },

    sentimentAnalysis: "تحليل المعنويات",
    realTimeAnalysis:
      "تحليل تلقائي للأخبار الاقتصادية وتقارير الأسواق والسياسات التجارية",
    noiseFilterActive: "مرشح التشويش نشط",
    noiseFiltered: "عنوان تمت تصفيته",
    sentimentBalance: "توازن المعنويات",
    noActiveSignals: "لا توجد إشارات نشطة",
    trend: "الاتجاه",
    rising: "صاعد",
    falling: "هابط",
    stable: "مستقر",

    topHeadlines: "أبرز العناوين المؤثرة على المعنويات",
    today: "اليوم",

    insights: "رؤى تحليلية",
    analysisPending: "التحليل قيد الإعداد",
    analysisPendingText:
      "جاري جمع البيانات للتحليل. ستظهر الرؤى التحليلية بعد توفر بيانات كافية",

    sentimentTrend24h: "اتجاه المعنويات خلال 24 ساعة",
    dataPoints: "نقطة بيانات",
    last24Hours: "آخر 24 ساعة",
    noHistoricalData:
      "لا تتوفر بيانات تاريخية حالياً. يتم جمع البيانات كل ساعة",

    connectionError: "خطأ في الاتصال",
    tryAgain: "إعادة المحاولة",

    footer: {
      createdBy: "تم التطوير بواسطة محمد عصام",
      repo: "المشروع على GitHub",
      disclaimer:
        "يتم جمع البيانات لأغراض التحليل فقط ولا يُعتبر نصيحة مالية أو استثمارية",
      builtBy: "تم التطوير بواسطة",
      hireText: "هل تحتاج إلى حلول تحليلية مخصصة؟",
    },
  },
};

export function getTranslation(locale: Locale): Translations {
  return translations[locale] || translations.en;
}

export function isRTL(locale: Locale): boolean {
  return locale === "ar";
}
