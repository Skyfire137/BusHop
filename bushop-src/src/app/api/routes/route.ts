// src/app/api/routes/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { fetchFromScraper } from '@/lib/scraper-client';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams.toString();
    const path = searchParams ? `/api/v1/routes?${searchParams}` : '/api/v1/routes';
    const data = await fetchFromScraper(path);
    return NextResponse.json(data);
  } catch (error) {
    console.error('[/api/routes] Error:', error);
    return NextResponse.json({ detail: 'Failed to fetch routes' }, { status: 500 });
  }
}
