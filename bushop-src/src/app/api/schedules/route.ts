// src/app/api/schedules/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { fetchFromScraper } from '@/lib/scraper-client';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams.toString();
    const path = searchParams
      ? `/api/v1/schedules?${searchParams}`
      : '/api/v1/schedules';
    const data = await fetchFromScraper(path);
    return NextResponse.json(data);
  } catch (error) {
    console.error('[/api/schedules] Error:', error);
    return NextResponse.json({ detail: 'Failed to fetch schedules' }, { status: 500 });
  }
}
