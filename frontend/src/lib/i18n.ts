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
  aiInsights: string;
  analysisPending: string;
  analysisPendingText: string;
  viewFullReport: string;

  // Trend chart
  sentimentTrend24h: string;
  dataPoints: string;
  last24Hours: string;
  noHistoricalData: string;

  // Errors
  connectionError: string;
  tryAgain: string;
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
      "Real-time AI analysis of economic news, market reports, and trade policies.",
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

    aiInsights: "AI Insights",
    analysisPending: "ANALYSIS PENDING",
    analysisPendingText:
      "Collecting data for AI analysis. Insights will appear after more data points are gathered.",
    viewFullReport: "View Full Report",

    sentimentTrend24h: "24h Sentiment Trend",
    dataPoints: "data points",
    last24Hours: "Last 24 Hours",
    noHistoricalData: "No historical data yet. Data is collected hourly.",

    connectionError: "Connection Error",
    tryAgain: "Try Again",
  },

  ar: {
    // Professional Arabic translations - formal business terminology
    appTitle: "مرصد التوجهات",
    appSubtitle: "نظرة شاملة على التوجهات الاقتصادية",
    systemOperational: "النظام فعّال",
    lastUpdated: "آخر تحديث",
    refresh: "تحديث البيانات",

    selectRegion: "اختيار المنطقة",
    headlines: "خبر",
    optimistic: "إيجابي",
    pessimistic: "سلبي",
    neutral: "محايد",

    regions: {
      global: "عالمي",
      us: "الولايات المتحدة الأمريكية",
      eu: "الاتحاد الأوروبي",
      africa: "أفريقيا",
      egypt: "جمهورية مصر العربية",
      saudi: "المملكة العربية السعودية",
      middleeast: "منطقة الشرق الأوسط",
    },

    regionDescriptions: {
      global: "الأخبار الاقتصادية العالمية",
      us: "الأسواق والاقتصاد الأمريكي",
      eu: "الأسواق والتجارة الأوروبية",
      africa: "التنمية والتجارة الأفريقية",
      egypt: "الاقتصاد المصري",
      saudi: "رؤية المملكة 2030 والاقتصاد",
      middleeast: "الأخبار الاقتصادية الإقليمية",
    },

    sentimentAnalysis: "تحليل التوجهات",
    realTimeAnalysis:
      "تحليل آني بالذكاء الاصطناعي للأخبار الاقتصادية وتقارير الأسواق والسياسات التجارية.",
    noiseFilterActive: "فلتر التصفية فعّال",
    noiseFiltered: "خبر تمت تصفيته",
    sentimentBalance: "ميزان التوجهات",
    noActiveSignals: "لا توجد مؤشرات فعّالة",
    trend: "الاتجاه",
    rising: "صاعد",
    falling: "هابط",
    stable: "مستقر",

    topHeadlines: "أبرز العناوين المؤثرة على التوجهات",
    today: "اليوم",

    aiInsights: "تحليلات الذكاء الاصطناعي",
    analysisPending: "التحليل قيد المعالجة",
    analysisPendingText:
      "جاري جمع البيانات للتحليل. ستظهر التحليلات بعد توفر بيانات كافية.",
    viewFullReport: "عرض التقرير الكامل",

    sentimentTrend24h: "اتجاه التوجهات خلال 24 ساعة",
    dataPoints: "نقطة بيانات",
    last24Hours: "آخر 24 ساعة",
    noHistoricalData:
      "لا تتوفر بيانات تاريخية حالياً. يتم جمع البيانات كل ساعة.",

    connectionError: "خطأ في الاتصال",
    tryAgain: "إعادة المحاولة",
  },
};

export function getTranslation(locale: Locale): Translations {
  return translations[locale] || translations.en;
}

export function isRTL(locale: Locale): boolean {
  return locale === "ar";
}
