/**
 * auth.ts
 *
 * 인증 관련 TypeScript 타입 정의
 *
 * TypeScript란?
 * - JavaScript에 타입을 추가한 언어
 * - 코드 작성 중에 에러를 미리 발견 가능
 * - 자동완성 지원으로 개발 속도 향상
 *
 * interface란?
 * - 객체의 구조(모양)를 정의하는 타입
 * - 어떤 속성들이 있고, 각 속성의 타입이 무엇인지 명시
 */

// 로그인 요청 데이터
export interface LoginRequest {
    email: string
    password: string
}

// 회원가입 요청 데이터
export interface RegisterRequest {
    email: string
    username: string
    password: string
}

// 비밀번호 변경 요청 데이터
export interface ChangePasswordRequest {
    current_password: string
    new_password: string
}

// 로그인 응답 데이터
export interface LoginResponse {
    access_token: string // JWT 토큰
    token_type: string // "bearer"
    user: User // 사용자 정보
}

// 사용자 정보
export interface User {
    id: number
    email: string
    username: string
    is_active: boolean // 활성화 여부 (관리자 승인)
    is_admin: boolean // 관리자 권한
    password_reset_required: boolean // 비밀번호 변경 필요 여부
    created_at: string // 가입일 (ISO 날짜 문자열)
}
