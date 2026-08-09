import { AxiosError } from 'axios';
import type { ApiResponse } from '../services/api';

export function getApiErrorMessage(error: unknown, fallback = 'Something went wrong'): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiResponse | { detail?: string | { msg: string }[] } | undefined;
    if (data && 'message' in data && data.message) {
      return data.message;
    }
    if (data && 'detail' in data) {
      const detail = data.detail;
      if (typeof detail === 'string') return detail;
      if (Array.isArray(detail)) {
        return detail.map((item) => (typeof item === 'string' ? item : item.msg)).join('; ');
      }
    }
    if (error.message) return error.message;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
