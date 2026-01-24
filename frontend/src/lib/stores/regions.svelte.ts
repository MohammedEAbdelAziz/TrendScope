/**
 * Svelte 5 runes-based store for region sentiment data
 */
import type { RegionSentiment } from "$lib/types";
import { REGION_CONFIGS } from "$lib/types";

// State using Svelte 5 runes
let regions = $state<RegionSentiment[]>([]);
let selectedRegionId = $state<string | null>(null);
let isLoading = $state(false);
let error = $state<string | null>(null);

// Derived state
const selectedRegion = $derived(
  regions.find((r) => r.region_id === selectedRegionId) ?? null,
);

const getRegionConfig = (regionId: string) =>
  REGION_CONFIGS.find((r) => r.id === regionId);

// Actions
function setRegions(data: RegionSentiment[]) {
  regions = data;
}

function selectRegion(regionId: string | null) {
  selectedRegionId = regionId;
}

function setLoading(loading: boolean) {
  isLoading = loading;
}

function setError(err: string | null) {
  error = err;
}

function reset() {
  regions = [];
  selectedRegionId = null;
  isLoading = false;
  error = null;
}

// Export the store object
export const regionsStore = {
  get regions() {
    return regions;
  },
  get selectedRegionId() {
    return selectedRegionId;
  },
  get selectedRegion() {
    return selectedRegion;
  },
  get isLoading() {
    return isLoading;
  },
  get error() {
    return error;
  },

  setRegions,
  selectRegion,
  setLoading,
  setError,
  reset,
  getRegionConfig,
};
