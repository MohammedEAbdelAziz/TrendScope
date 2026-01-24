/**
 * API client for the Econ-Mood Monitor backend
 */
import type { APIResponse, RegionSentiment } from "./types";

const API_BASE_URL = ""; // Uses SvelteKit server-side proxy routes

// Trend data types
export interface TrendDataPoint {
  score: number;
  label: string;
  headline_count: number;
  timestamp: string;
}

export interface TrendResponse {
  success: boolean;
  region_id: string;
  trend: "rising" | "falling" | "stable";
  change: number;
  data_points: number;
  data: TrendDataPoint[];
}

// AI Insights types
export interface InsightItem {
  title: string;
  text: string;
  color: string;
  icon: string;
}

export interface InsightsResponse {
  success: boolean;
  region_id: string;
  insights: InsightItem[];
}

export async function fetchAllRegions(): Promise<RegionSentiment[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/regions`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: APIResponse = await response.json();

    if (!data.success || !data.data) {
      throw new Error(data.error || "Failed to fetch regions");
    }

    return data.data;
  } catch (error) {
    console.error("Error fetching regions:", error);
    throw error;
  }
}

export async function fetchRegion(regionId: string): Promise<RegionSentiment> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/regions/${regionId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: APIResponse = await response.json();

    if (!data.success || !data.data || data.data.length === 0) {
      throw new Error(data.error || "Failed to fetch region");
    }

    return data.data[0];
  } catch (error) {
    console.error(`Error fetching region ${regionId}:`, error);
    throw error;
  }
}

export async function fetchTrend(
  regionId: string,
  hours: number = 24,
): Promise<TrendResponse> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/regions/${regionId}/trend?hours=${hours}`,
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error fetching trend for ${regionId}:`, error);
    throw error;
  }
}

export async function fetchInsights(
  regionId: string,
): Promise<InsightsResponse> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/regions/${regionId}/insights`,
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error fetching insights for ${regionId}:`, error);
    throw error;
  }
}

export async function triggerCollection(): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/collect`, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error("Error triggering collection:", error);
    throw error;
  }
}

export async function refreshCache(): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/refresh`, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error("Error refreshing cache:", error);
    throw error;
  }
}
