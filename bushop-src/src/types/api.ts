// Field names mirror the wire format (snake_case from FastAPI/Pydantic).
// Do not rename to camelCase without adding a mapping layer.

// src/types/api.ts
export interface ApiMeta {
  scraped_at: string | null; // ISO 8601 or null
}

export interface ApiResponse<T> {
  data: T;
  meta: ApiMeta;
}
