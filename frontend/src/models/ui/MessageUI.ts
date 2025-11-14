import type {MessageModel} from '../MessageModel'

/**
 * UI 표시용 메시지 모델
 * - MessageModel에 UI 관련 속성 추가
 */
export interface MessageUI extends MessageModel {
    clientId: number // ⚠️ UI 렌더링용 고유 ID (React key로 사용)
    timestamp: Date
    isOutline?: boolean // Outline 모드 여부 (개요 표시용)
    reportData?: {
        // md 아티팩트 내용
        reportId?: number
        filename?: string
        content?: string
    }
}
