// src/types/schedule.ts
import type { ApiResponse } from './api';

export interface Schedule {
  id: string;
  route_id: number;
  operator_name: string;
  departure_time: string;
  arrival_time: string;
  price: number;
  scraped_at: string;
  is_stale: boolean;
}

export type SchedulesResponse = ApiResponse<Schedule[]>;

export interface ScheduleSearchParams {
  origin_id: number;
  destination_id: number;
  date: string;
}

export interface BusResultCardProps {
  id: string;
  provider: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  price_jpy: number;
  seat_type: string;
  seats_available: number | null;
  is_cheapest?: boolean;
  affiliate_url: string;
  pickup_location: string;
  pickup_lat?: number;
  pickup_lng?: number;
  dropoff_location: string;
}
