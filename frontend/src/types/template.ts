/**
 * types/template.ts
 *
 * 템플릿 관련 TypeScript 타입 정의
 */

/**
 * 템플릿 엔티티 (DB 모델)
 */
export interface Template {
    id: number
    user_id: number
    title: string
    description?: string
    filename: string
    file_path: string
    file_size: number
    sha256: string
    is_active: boolean
    created_at: string
    updated_at: string
}

/**
 * 플레이스홀더 엔티티
 */
export interface Placeholder {
    id: number
    template_id: number
    placeholder_key: string
    created_at: string
}

/**
 * 템플릿 목록 아이템 (간소화된 버전)
 */
export interface TemplateListItem {
    id: number
    title: string
    filename: string
    file_size: number
    created_at: string
}

/**
 * 템플릿 상세 정보 (플레이스홀더 포함)
 */
export interface TemplateDetail {
    id: number
    title: string
    filename: string
    file_size: number
    placeholders: Array<{key: string}>
    created_at: string
}

/**
 * 템플릿 업로드 요청
 */
export interface TemplateUploadRequest {
    file: File
    title: string
}

/**
 * 템플릿 업로드 응답
 */
export interface UploadTemplateResponse {
    id: number
    title: string
    filename: string
    file_size: number
    placeholders: Array<{key: string}>
    created_at: string
}

/**
 * 관리자: 템플릿 목록 아이템
 */
export interface AdminTemplateItem {
    id: number
    title: string
    username: string
    file_size: number
    placeholder_count: number
    created_at: string
}

/**
 * 템플릿 삭제 응답
 */
export interface DeleteTemplateResponse {
    id: number
    message: string
}
