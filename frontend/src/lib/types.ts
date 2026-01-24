/**
 * Type definitions for the Econ-Mood Monitor
 */

export type SentimentLabel = "positive" | "neutral" | "negative";

export interface Headline {
  title: string;
  source: string;
  url: string;
  published_at: string | null;
  sentiment_score: number;
  sentiment_label: SentimentLabel;
}

export interface RegionSentiment {
  region_id: string;
  region_name: string;
  sentiment_score: number;
  sentiment_label: SentimentLabel;
  headline_count: number;
  // Polarity counts
  bull_count: number;
  bear_count: number;
  neutral_count: number;
  filtered_count: number;
  top_headlines: Headline[];
  last_updated: string;
}

export interface APIResponse {
  success: boolean;
  data: RegionSentiment[] | null;
  error: string | null;
  timestamp: string;
}

export interface RegionConfig {
  id: string;
  name: string;
  icon: string; // Lucide icon name
  description: string;
}

export const REGION_CONFIGS: RegionConfig[] = [
  {
    id: "global",
    name: "Global",
    icon: "Globe2",
    description: "Worldwide Economic News",
  },
  {
    id: "us",
    name: "United States",
    icon: "Building2",
    description: "US Markets & Economy",
  },
  {
    id: "eu",
    name: "European Union",
    icon: "Landmark",
    description: "European Markets & Trade",
  },
  {
    id: "africa",
    name: "Africa",
    icon: "Map",
    description: "African Development & Trade",
  },
  {
    id: "egypt",
    name: "Egypt",
    icon: "Pyramid",
    description: "Egyptian Economy",
  },
  {
    id: "saudi",
    name: "Saudi Arabia",
    icon: "Building",
    description: "Saudi Vision 2030 & Economy",
  },
  {
    id: "middleeast",
    name: "Middle East",
    icon: "MapPin",
    description: "Regional Economic News",
  },
];
