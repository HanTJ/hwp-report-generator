/**
 * 백엔드 표준 API Response 형식
 * CLAUDE.md 참고
 */

export type FeedbackLevel = 'info' | 'warning' | 'error';

export interface Feedback {
  code: string;
  level: FeedbackLevel;
  feedbackCd: string;
}

export interface ErrorResponse {
  code: string;
  httpStatus: number;
  message: string;
  details?: Record<string, any>;
  traceId: string;
  hint?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data: T | null;
  error: ErrorResponse | null;
  meta: {
    requestId: string;
  };
  feedback: Feedback[];
}

// Legacy - 호환성 유지용
export interface ApiError {
  detail: string;
}
