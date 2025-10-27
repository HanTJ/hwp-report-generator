/**
 * API 공통 상수
 * constants.properties 파일의 TypeScript 버전
 */

// ============================================================
// 에러 코드
// ============================================================

export const ErrorCode = {
  AUTH: {
    INVALID_TOKEN: 'AUTH.INVALID_TOKEN',
    TOKEN_EXPIRED: 'AUTH.TOKEN_EXPIRED',
    UNAUTHORIZED: 'AUTH.UNAUTHORIZED',
    FORBIDDEN: 'AUTH.FORBIDDEN',
    INVALID_CREDENTIALS: 'AUTH.INVALID_CREDENTIALS',
    USER_NOT_FOUND: 'AUTH.USER_NOT_FOUND',
    PASSWORD_MISMATCH: 'AUTH.PASSWORD_MISMATCH',
  },
  VALIDATION: {
    ERROR: 'VALIDATION.ERROR',
    MISSING_FIELD: 'VALIDATION.MISSING_FIELD',
    INVALID_FORMAT: 'VALIDATION.INVALID_FORMAT',
    FIELD_TOO_SHORT: 'VALIDATION.FIELD_TOO_SHORT',
    FIELD_TOO_LONG: 'VALIDATION.FIELD_TOO_LONG',
    INVALID_EMAIL: 'VALIDATION.INVALID_EMAIL',
    INVALID_TYPE: 'VALIDATION.INVALID_TYPE',
  },
  REPORT: {
    GENERATION_FAILED: 'REPORT.GENERATION_FAILED',
    NOT_FOUND: 'REPORT.NOT_FOUND',
    TOPIC_TOO_SHORT: 'REPORT.TOPIC_TOO_SHORT',
    TOPIC_EMPTY: 'REPORT.TOPIC_EMPTY',
    GENERATION_TIMEOUT: 'REPORT.GENERATION_TIMEOUT',
    INVALID_TEMPLATE: 'REPORT.INVALID_TEMPLATE',
  },
  HWP: {
    PROCESSING_ERROR: 'HWP.PROCESSING_ERROR',
    TEMPLATE_NOT_FOUND: 'HWP.TEMPLATE_NOT_FOUND',
    INVALID_FORMAT: 'HWP.INVALID_FORMAT',
    EXTRACTION_FAILED: 'HWP.EXTRACTION_FAILED',
    COMPRESSION_FAILED: 'HWP.COMPRESSION_FAILED',
    XML_PARSE_ERROR: 'HWP.XML_PARSE_ERROR',
  },
  CLAUDE: {
    API_ERROR: 'CLAUDE.API_ERROR',
    RATE_LIMIT: 'CLAUDE.RATE_LIMIT',
    TIMEOUT: 'CLAUDE.TIMEOUT',
    INVALID_RESPONSE: 'CLAUDE.INVALID_RESPONSE',
    CONNECTION_ERROR: 'CLAUDE.CONNECTION_ERROR',
    QUOTA_EXCEEDED: 'CLAUDE.QUOTA_EXCEEDED',
  },
  FILE: {
    NOT_FOUND: 'FILE.NOT_FOUND',
    UPLOAD_FAILED: 'FILE.UPLOAD_FAILED',
    SIZE_EXCEEDED: 'FILE.SIZE_EXCEEDED',
    INVALID_TYPE: 'FILE.INVALID_TYPE',
    DOWNLOAD_FAILED: 'FILE.DOWNLOAD_FAILED',
  },
  SYSTEM: {
    INTERNAL_ERROR: 'SYSTEM.INTERNAL_ERROR',
    SERVICE_UNAVAILABLE: 'SYSTEM.SERVICE_UNAVAILABLE',
    DATABASE_ERROR: 'SYSTEM.DATABASE_ERROR',
    NETWORK_ERROR: 'SYSTEM.NETWORK_ERROR',
    TIMEOUT: 'SYSTEM.TIMEOUT',
  },
} as const;

// 타입 추론
export type ErrorCodeType = typeof ErrorCode[keyof typeof ErrorCode][keyof typeof ErrorCode[keyof typeof ErrorCode]];


// ============================================================
// 피드백 코드
// ============================================================

export const FeedbackCode = {
  PROFILE: {
    INCOMPLETE: 'PROFILE.INCOMPLETE',
    PHOTO_MISSING: 'PROFILE.PHOTO_MISSING',
    UPDATE_SUCCESS: 'PROFILE.UPDATE_SUCCESS',
  },
  REPORT: {
    GENERATION_SUCCESS: 'REPORT.GENERATION_SUCCESS',
    GENERATION_IN_PROGRESS: 'REPORT.GENERATION_IN_PROGRESS',
    TOPIC_SUGGESTION: 'REPORT.TOPIC_SUGGESTION',
    TEMPLATE_UPDATED: 'REPORT.TEMPLATE_UPDATED',
  },
  SYSTEM: {
    MAINTENANCE_SCHEDULED: 'SYSTEM.MAINTENANCE_SCHEDULED',
    NEW_FEATURE: 'SYSTEM.NEW_FEATURE',
    UPDATE_AVAILABLE: 'SYSTEM.UPDATE_AVAILABLE',
  },
  SECURITY: {
    PASSWORD_EXPIRING: 'SECURITY.PASSWORD_EXPIRING',
    UNUSUAL_LOGIN: 'SECURITY.UNUSUAL_LOGIN',
    TWO_FACTOR_RECOMMENDED: 'SECURITY.TWO_FACTOR_RECOMMENDED',
  },
} as const;


// ============================================================
// 피드백 레벨
// ============================================================

export const FeedbackLevel = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
} as const;

export type FeedbackLevelType = typeof FeedbackLevel[keyof typeof FeedbackLevel];


// ============================================================
// HTTP 상태 코드
// ============================================================

export const HttpStatus = {
  // 2xx Success
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,

  // 4xx Client Error
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,

  // 5xx Server Error
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;


// ============================================================
// API 메시지
// ============================================================

export const Message = {
  SUCCESS: {
    REPORT_GENERATED: '보고서가 성공적으로 생성되었습니다.',
    LOGIN_SUCCESS: '로그인되었습니다.',
    LOGOUT_SUCCESS: '로그아웃되었습니다.',
    PROFILE_UPDATED: '프로필이 업데이트되었습니다.',
  },
  ERROR: {
    INVALID_TOKEN: '유효하지 않은 토큰입니다.',
    TOKEN_EXPIRED: '토큰이 만료되었습니다.',
    UNAUTHORIZED: '인증이 필요합니다.',
    FORBIDDEN: '접근 권한이 없습니다.',
    REPORT_GENERATION_FAILED: '보고서 생성에 실패했습니다.',
    TOPIC_TOO_SHORT: '보고서 주제는 10자 이상이어야 합니다.',
    TOPIC_EMPTY: '보고서 주제를 입력해주세요.',
    INTERNAL_ERROR: '서버 오류가 발생했습니다.',
    SERVICE_UNAVAILABLE: '서비스를 일시적으로 사용할 수 없습니다.',
    INVALID_CREDENTIALS: '아이디 또는 비밀번호가 올바르지 않습니다.',
    USER_NOT_FOUND: '사용자를 찾을 수 없습니다.',
    HWP_TEMPLATE_NOT_FOUND: 'HWP 템플릿 파일을 찾을 수 없습니다.',
    CLAUDE_API_ERROR: 'AI 콘텐츠 생성 중 오류가 발생했습니다.',
    CLAUDE_RATE_LIMIT: 'API 요청 한도를 초과했습니다.',
  },
  HINT: {
    LOGIN_AGAIN: '다시 로그인해 주세요.',
    CONTACT_ADMIN: '관리자에게 문의하세요.',
    TRY_AGAIN_LATER: '잠시 후 다시 시도해 주세요.',
    CHECK_INPUT: '입력값을 확인해 주세요.',
    CHECK_TEMPLATE: 'HWP 템플릿 파일이 올바른 위치에 있는지 확인하세요.',
    REDUCE_REQUEST_RATE: '요청 빈도를 줄여주세요.',
  },
} as const;


// ============================================================
// 검증 제약조건
// ============================================================

export const ValidationConstraint = {
  REPORT_TOPIC: {
    MIN_LENGTH: 10,
    MAX_LENGTH: 200,
  },
  PASSWORD: {
    MIN_LENGTH: 8,
    MAX_LENGTH: 50,
  },
  EMAIL: {
    REGEX: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  },
  FILE: {
    MAX_SIZE_MB: 10,
  },
} as const;


// ============================================================
// 토큰 설정
// ============================================================

export const TokenConfig = {
  ACCESS_TOKEN_EXPIRE_MINUTES: 15,
  REFRESH_TOKEN_EXPIRE_DAYS: 7,
  ALGORITHM: 'HS256',
} as const;


// ============================================================
// API 엔드포인트
// ============================================================

export const Endpoint = {
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
  },
  REPORT: {
    GENERATE: '/api/report/generate',
    DOWNLOAD: '/api/report/download',
  },
  USER: {
    PROFILE: '/api/user/profile',
  },
} as const;


// ============================================================
// 쿠키 설정
// ============================================================

export const CookieConfig = {
  REFRESH_TOKEN: {
    NAME: 'refreshToken',
    HTTPONLY: true,
    SECURE: true,
    SAMESITE: 'strict' as const,
    MAX_AGE: 604800, // 7일 (초 단위)
  },
} as const;


// ============================================================
// 비즈니스 규칙
// ============================================================

export const BusinessRule = {
  REPORT: {
    DEFAULT_DATE_FORMAT: 'YYYY년 MM월 DD일',
    OUTPUT_DIRECTORY: 'output',
    TEMP_DIRECTORY: 'temp',
    TEMPLATE_PATH: 'templates/report_template.hwpx',
    GENERATION_TIMEOUT_SECONDS: 60,
  },
} as const;


// ============================================================
// Claude API 설정
// ============================================================

export const ClaudeConfig = {
  MODEL: 'claude-sonnet-4-5-20250929',
  MAX_TOKENS: 4096,
  TEMPERATURE: 1.0,
  TIMEOUT_SECONDS: 60,
} as const;


// ============================================================
// 피드백 메시지
// ============================================================

export const FeedbackMessage = {
  PROFILE_INCOMPLETE: '프로필 사진을 등록하면 더 좋아요.',
  PROFILE_PHOTO_MISSING: '프로필 사진을 추가해보세요.',
  REPORT_GENERATION_SUCCESS: '보고서 생성이 완료되었습니다.',
  REPORT_GENERATION_IN_PROGRESS: '보고서를 생성 중입니다. 잠시만 기다려주세요.',
  PASSWORD_EXPIRING: '비밀번호 변경 후 30일이 지났습니다.',
  MAINTENANCE_SCHEDULED: '2025년 10월 25일 02:00-04:00 시스템 점검이 예정되어 있습니다.',
  NEW_FEATURE: '새로운 기능이 추가되었습니다. 확인해보세요!',
} as const;


// ============================================================
// 헬퍼 함수
// ============================================================

/**
 * 에러 코드에 해당하는 메시지 반환
 */
export const getErrorMessage = (errorCode: string): string => {
  const errorMessageMap: Record<string, string> = {
    [ErrorCode.AUTH.INVALID_TOKEN]: Message.ERROR.INVALID_TOKEN,
    [ErrorCode.AUTH.TOKEN_EXPIRED]: Message.ERROR.TOKEN_EXPIRED,
    [ErrorCode.AUTH.UNAUTHORIZED]: Message.ERROR.UNAUTHORIZED,
    [ErrorCode.AUTH.FORBIDDEN]: Message.ERROR.FORBIDDEN,
    [ErrorCode.AUTH.INVALID_CREDENTIALS]: Message.ERROR.INVALID_CREDENTIALS,
    [ErrorCode.REPORT.GENERATION_FAILED]: Message.ERROR.REPORT_GENERATION_FAILED,
    [ErrorCode.REPORT.TOPIC_TOO_SHORT]: Message.ERROR.TOPIC_TOO_SHORT,
    [ErrorCode.REPORT.TOPIC_EMPTY]: Message.ERROR.TOPIC_EMPTY,
    [ErrorCode.HWP.TEMPLATE_NOT_FOUND]: Message.ERROR.HWP_TEMPLATE_NOT_FOUND,
    [ErrorCode.CLAUDE.API_ERROR]: Message.ERROR.CLAUDE_API_ERROR,
    [ErrorCode.CLAUDE.RATE_LIMIT]: Message.ERROR.CLAUDE_RATE_LIMIT,
  };
  return errorMessageMap[errorCode] || Message.ERROR.INTERNAL_ERROR;
};

/**
 * 에러 코드에 해당하는 힌트 반환
 */
export const getErrorHint = (errorCode: string): string => {
  const errorHintMap: Record<string, string> = {
    [ErrorCode.AUTH.INVALID_TOKEN]: Message.HINT.LOGIN_AGAIN,
    [ErrorCode.AUTH.TOKEN_EXPIRED]: Message.HINT.LOGIN_AGAIN,
    [ErrorCode.AUTH.UNAUTHORIZED]: Message.HINT.LOGIN_AGAIN,
    [ErrorCode.VALIDATION.ERROR]: Message.HINT.CHECK_INPUT,
    [ErrorCode.HWP.TEMPLATE_NOT_FOUND]: Message.HINT.CHECK_TEMPLATE,
    [ErrorCode.CLAUDE.RATE_LIMIT]: Message.HINT.REDUCE_REQUEST_RATE,
    [ErrorCode.SYSTEM.INTERNAL_ERROR]: Message.HINT.TRY_AGAIN_LATER,
  };
  return errorHintMap[errorCode] || Message.HINT.CONTACT_ADMIN;
};


// ============================================================
// API 응답 타입 정의
// ============================================================

export interface ApiFeedback {
  code: string;
  level: FeedbackLevelType;
  message: string;
  messageKey?: string;
}

export interface ApiError {
  code: string;
  httpStatus: number;
  message: string;
  details?: Record<string, any>;
  traceId?: string;
  hint?: string;
}

export interface ApiMeta {
  requestId: string;
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    hasNext: boolean;
  };
  rateLimit?: {
    remaining: number;
    resetAt: string;
  };
}

export interface ApiResponse<T = any> {
  success: boolean;
  data: T | null;
  error: ApiError | null;
  meta: ApiMeta;
  timestamp: string;
  feedback: ApiFeedback[];
}


// ============================================================
// 응답 생성 헬퍼 함수 (클라이언트용)
// ============================================================

/**
 * API 에러인지 확인
 */
export const isApiError = (response: ApiResponse): response is ApiResponse & { success: false; error: ApiError } => {
  return !response.success && response.error !== null;
};

/**
 * API 성공 응답인지 확인
 */
export const isApiSuccess = <T>(response: ApiResponse<T>): response is ApiResponse<T> & { success: true; data: T } => {
  return response.success && response.data !== null;
};
