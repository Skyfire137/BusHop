// src/types/route.ts
import type { ApiResponse } from './api';

export interface ProvinceI18n {
  vi: string;
  en: string;
  ja: string;
}

export interface Route {
  id: number;
  slug: string;
  origin_id: number;
  destination_id: number;
  origin_name: ProvinceI18n;
  destination_name: ProvinceI18n;
}

export type RoutesResponse = ApiResponse<Route[]>;
