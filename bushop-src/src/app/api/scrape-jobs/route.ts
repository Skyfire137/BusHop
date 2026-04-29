// src/app/api/scrape-jobs/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { fetchFromScraper } from '@/lib/scraper-client';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams.toString();
    const path = searchParams
      ? `/api/v1/scrape-jobs?${searchParams}`
      : '/api/v1/scrape-jobs';
    const data = await fetchFromScraper(path);
    return NextResponse.json(data);
  } catch (error) {
    console.error('[/api/scrape-jobs GET] Error:', error);
    return NextResponse.json({ detail: 'Failed to fetch scrape jobs' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const data = await fetchFromScraper('/api/v1/scrape-jobs', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return NextResponse.json(data);
  } catch (error) {
    console.error('[/api/scrape-jobs POST] Error:', error);
    return NextResponse.json({ detail: 'Failed to create scrape job' }, { status: 500 });
  }
}
