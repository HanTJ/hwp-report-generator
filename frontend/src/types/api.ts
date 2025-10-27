/**
 * API Response Standard Types
 * Based on API 공통 규격 양식 from CLAUDE.md
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

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface UserResponse {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_admin: boolean;
  password_reset_required: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface PasswordChangeRequest {
  old_password: string;
  new_password: string;
}

// Report Types
export interface ReportCreate {
  topic: string;
}

export interface ReportResponse {
  id: number;
  user_id: number;
  topic: string;
  title: string;
  filename: string;
  file_size: number;
  created_at: string;
}

export interface ReportListResponse {
  total: number;
  reports: ReportResponse[];
}

// Admin Types
export interface UserUpdate {
  is_active?: boolean;
  is_admin?: boolean;
  password_reset_required?: boolean;
}

export interface UserTokenStats {
  user_id: number;
  username: string;
  email: string;
  total_reports: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_tokens: number;
}

export interface PasswordResetResponse {
  message: string;
  temporary_password: string;
}

// Error Codes (for reference)
export const ERROR_CODES = {
  // Authentication
  AUTH: {
    INVALID_TOKEN: 'AUTH.INVALID_TOKEN',
    TOKEN_EXPIRED: 'AUTH.TOKEN_EXPIRED',
    UNAUTHORIZED: 'AUTH.UNAUTHORIZED',
    INVALID_CREDENTIALS: 'AUTH.INVALID_CREDENTIALS',
  },
  // Reports
  REPORT: {
    GENERATION_FAILED: 'REPORT.GENERATION_FAILED',
    NOT_FOUND: 'REPORT.NOT_FOUND',
    INVALID_TOPIC: 'REPORT.INVALID_TOPIC',
    DOWNLOAD_FAILED: 'REPORT.DOWNLOAD_FAILED',
  },
  // Templates
  TEMPLATE: {
    INVALID_FORMAT: 'TEMPLATE.INVALID_FORMAT',
    UPLOAD_FAILED: 'TEMPLATE.UPLOAD_FAILED',
    NOT_FOUND: 'TEMPLATE.NOT_FOUND',
    PERMISSION_DENIED: 'TEMPLATE.PERMISSION_DENIED',
  },
  // Validation
  VALIDATION: {
    REQUIRED_FIELD: 'VALIDATION.REQUIRED_FIELD',
    INVALID_FORMAT: 'VALIDATION.INVALID_FORMAT',
    MAX_LENGTH_EXCEEDED: 'VALIDATION.MAX_LENGTH_EXCEEDED',
  },
  // Server
  SERVER: {
    INTERNAL_ERROR: 'SERVER.INTERNAL_ERROR',
    SERVICE_UNAVAILABLE: 'SERVER.SERVICE_UNAVAILABLE',
    DATABASE_ERROR: 'SERVER.DATABASE_ERROR',
  },
} as const;
