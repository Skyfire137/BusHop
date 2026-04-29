// src/types/scrape-job.ts
import type { ApiResponse } from './api';

export type ScrapeJobStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface ScrapeJob {
  id: string;
  status: ScrapeJobStatus;
  route_id: number;
  created_at: string;
  completed_at: string | null;
}

export type ScrapeJobResponse = ApiResponse<ScrapeJob>;

export interface CreateScrapeJobRequest {
  route_id: number;
  travel_date: string;
}
