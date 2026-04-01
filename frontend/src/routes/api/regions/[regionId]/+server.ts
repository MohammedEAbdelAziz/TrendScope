import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

const BACKEND_URL = process.env.PUBLIC_API_URL || "http://backend:8000";
const BACKEND_TIMEOUT_MS = 8000;

export const GET: RequestHandler = async ({ params, url, fetch }) => {
  const regionId = params.regionId;
  const queryString = url.search;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), BACKEND_TIMEOUT_MS);

  try {
    const response = await fetch(
      `${BACKEND_URL}/api/regions/${regionId}${queryString}`,
      {
        signal: controller.signal,
      },
    );
    const data = await response.json();
    return json(data, { status: response.status });
  } catch (error) {
    console.error(`Error proxying to backend for region ${regionId}:`, error);
    const isTimeout = error instanceof Error && error.name === "AbortError";
    return json(
      {
        success: false,
        error: isTimeout
          ? "Backend request timed out"
          : "Failed to connect to backend",
      },
      { status: isTimeout ? 504 : 502 },
    );
  } finally {
    clearTimeout(timeout);
  }
};
