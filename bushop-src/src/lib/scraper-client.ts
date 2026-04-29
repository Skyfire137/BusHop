// src/lib/scraper-client.ts
// SERVER-SIDE ONLY — do not import this file in Client Components.
// Browser code must call Next.js proxy routes (/api/routes, /api/schedules, etc.)
// and never reference SCRAPER_API_URL or INTERNAL_API_KEY directly.

export async function fetchFromScraper(
  path: string,
  options?: RequestInit,
): Promise<unknown> {
  const baseUrl = process.env.SCRAPER_API_URL;
  if (!baseUrl) {
    throw new Error('SCRAPER_API_URL is not configured');
  }

  const apiKey = process.env.INTERNAL_API_KEY;
  if (!apiKey) {
    throw new Error('INTERNAL_API_KEY is not configured');
  }

  const res = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      ...options?.headers,
      'Content-Type': 'application/json',
      'X-Internal-API-Key': apiKey,
    },
  });

  if (res.status === 401) {
    throw new Error('Scraper API authentication failed — check INTERNAL_API_KEY');
  }

  if (!res.ok) {
    throw new Error(`Scraper API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}
