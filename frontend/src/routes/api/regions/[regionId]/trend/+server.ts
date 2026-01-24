import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

const BACKEND_URL = process.env.PUBLIC_API_URL || "http://backend:8000";

export const GET: RequestHandler = async ({ params, fetch }) => {
  const regionId = params.regionId;

  try {
    const response = await fetch(
      `${BACKEND_URL}/api/regions/${regionId}/trend`,
    );
    const data = await response.json();
    return json(data);
  } catch (error) {
    console.error(`Error proxying trend for region ${regionId}:`, error);
    return json(
      { success: false, error: "Failed to connect to backend" },
      { status: 500 },
    );
  }
};
