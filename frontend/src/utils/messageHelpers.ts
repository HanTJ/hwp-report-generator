import {artifactApi} from '../services/artifactApi'
import type {Artifact} from '../types/artifact'

/**
 * messageHelpers.ts
 *
 * 메시지 관련 유틸리티 함수
 * - 메시지와 아티팩트 연결
 * - backend 메시지 형태를 UI 메시지로 변환
 */

export interface Message {
    id: string
    messageId: number
    type: 'user' | 'assistant'
    content: string
    reportData?: {
        filename: string
        reportId: number
        messageId: number
        content: string
    }
    timestamp: Date
}

/**
 * 단일 메시지에 관련 아티팩트 내용을 연결합니다.
 *
 * Assistant 메시지에 연결된 마크다운(MD) 형식의 아티팩트가 있을 경우,
 * 해당 아티팩트의 실제 내용을 API로부터 가져와 메시지 객체에 포함시킵니다.
 *
 * @param msg - 아티팩트를 연결할 메시지 객체
 * @param artifacts - 검색 대상 아티팩트 배열
 * @returns 아티팩트 내용이 포함된 메시지 객체 (Promise)
 *
 * @example
 * // Assistant 메시지에 MD 아티팩트가 연결된 경우
 * const message: Message = {
 *   id: '1',
 *   messageId: 10,
 *   type: 'assistant',
 *   content: '보고서를 생성했습니다.',
 *   timestamp: new Date()
 * }
 * const artifacts: Artifact[] = [
 *   { id: 5, kind: 'md', message_id: 10, filename: 'report.md', ... }
 * ]
 * const enriched = await enrichMessageWithArtifact(message, artifacts)
 * // enriched.reportData = {
 * //   filename: 'report.md',
 * //   reportId: 5,
 * //   messageId: 10,
 * //   content: '# 보고서 내용...'
 * // }
 *
 * @example
 * // User 메시지 또는 연결된 아티팩트가 없는 경우
 * const userMessage: Message = {
 *   id: '2',
 *   messageId: 11,
 *   type: 'user',
 *   content: '보고서를 생성해주세요.',
 *   timestamp: new Date()
 * }
 * const result = await enrichMessageWithArtifact(userMessage, [])
 * // result === userMessage (변경 없음)
 *
 * @remarks
 * - Assistant 메시지만 아티팩트 연결 대상 (User 메시지는 무시)
 * - 'md' 종류의 아티팩트만 처리
 * - API 호출 실패 시 원본 메시지 반환 (에러 로깅만 수행)
 * - 하나의 메시지에 여러 아티팩트가 있을 경우 첫 번째 매칭 항목만 사용
 */
export const enrichMessageWithArtifact = async (msg: Message, artifacts: Artifact[]): Promise<Message> => {
    // 이 메시지와 연결된 MD 아티팩트 찾기
    const relatedArtifact = artifacts.find((art) => art.kind === 'md' && art.message_id === msg.messageId)

    // assistant 메시지에 아티팩트가 있으면 내용 로드
    if (relatedArtifact && msg.type === 'assistant') {
        try {
            const contentResponse = await artifactApi.getArtifactContent(relatedArtifact.id)
            return {
                ...msg,
                reportData: {
                    filename: relatedArtifact.filename,
                    reportId: relatedArtifact.id,
                    messageId: msg.messageId,
                    content: contentResponse.content
                }
            }
        } catch (error) {
            console.error('Failed to load artifact content:', error)
            return msg
        }
    }

    return msg
}

/**
 * 여러 메시지에 아티팩트 내용을 일괄 연결합니다.
 *
 * 메시지 배열의 각 항목에 대해 `enrichMessageWithArtifact`를 병렬로 실행하여
 * 모든 관련 아티팩트 내용을 동시에 로드합니다.
 *
 * @param messages - 아티팩트를 연결할 메시지 배열
 * @param artifacts - 검색 대상 아티팩트 배열
 * @returns 아티팩트 내용이 포함된 메시지 배열 (Promise)
 *
 * @example
 * const messages: Message[] = [
 *   { id: '1', messageId: 10, type: 'user', content: '요청', timestamp: new Date() },
 *   { id: '2', messageId: 11, type: 'assistant', content: '응답', timestamp: new Date() }
 * ]
 * const artifacts: Artifact[] = [
 *   { id: 5, kind: 'md', message_id: 11, filename: 'report.md', ... }
 * ]
 * const enrichedMessages = await enrichMessagesWithArtifacts(messages, artifacts)
 * // enrichedMessages[0]: 아티팩트 없음 (user 메시지)
 * // enrichedMessages[1]: reportData 포함 (assistant 메시지 + 아티팩트)
 *
 * @remarks
 * - 내부적으로 `Promise.all`을 사용하여 병렬 처리
 * - 각 메시지는 독립적으로 처리되며, 일부 실패해도 나머지는 정상 처리됨
 * - 빈 배열을 전달하면 빈 배열 반환
 */
export const enrichMessagesWithArtifacts = async (messages: Message[], artifacts: Artifact[]): Promise<Message[]> => {
    return Promise.all(messages.map((msg) => enrichMessageWithArtifact(msg, artifacts)))
}

/**
 * 백엔드 API 응답 메시지를 UI용 Message 형식으로 변환합니다.
 *
 * 백엔드에서 반환되는 메시지 객체의 필드명과 타입을 프론트엔드
 * UI 컴포넌트에서 사용하는 형식으로 매핑합니다.
 *
 * @param msg - 백엔드 API로부터 받은 메시지 객체
 *   - msg.id: 메시지 고유 ID (number)
 *   - msg.role: 메시지 역할 ('user' | 'assistant')
 *   - msg.content: 메시지 내용 (string)
 *   - msg.created_at: 생성 시간 (ISO 8601 문자열)
 * @returns UI용 Message 객체
 *
 * @example
 * // 백엔드 응답
 * const backendMessage = {
 *   id: 42,
 *   role: 'assistant',
 *   content: '보고서를 생성했습니다.',
 *   created_at: '2025-01-15T10:30:00Z'
 * }
 *
 * const uiMessage = toUIMessage(backendMessage)
 * // {
 * //   id: '42',
 * //   messageId: 42,
 * //   type: 'assistant',
 * //   content: '보고서를 생성했습니다.',
 * //   timestamp: Date 객체
 * // }
 *
 * @example
 * // User 메시지 변환
 * const userBackendMessage = {
 *   id: 41,
 *   role: 'user',
 *   content: '2025년 디지털뱅킹 트렌드 보고서',
 *   created_at: '2025-01-15T10:29:50Z'
 * }
 *
 * const userUIMessage = toUIMessage(userBackendMessage)
 * // {
 * //   id: '41',
 * //   messageId: 41,
 * //   type: 'user',
 * //   content: '2025년 디지털뱅킹 트렌드 보고서',
 * //   timestamp: Date 객체
 * // }
 *
 * @remarks
 * - 백엔드 `role` 필드를 UI `type` 필드로 매핑
 * - 숫자 ID를 문자열로 변환 (`id` 필드)
 * - ISO 8601 문자열을 Date 객체로 변환
 * - `reportData`는 이 함수에서 추가되지 않음 (enrichMessageWithArtifact 사용)
 */
export const toUIMessage = (msg: any): Message => ({
    id: msg.id.toString(),
    messageId: msg.id,
    type: msg.role === 'user' ? 'user' : 'assistant',
    content: msg.content,
    timestamp: new Date(msg.created_at)
})

/**
 * 백엔드 API 응답 메시지 배열을 UI용 Message 배열로 일괄 변환합니다.
 *
 * 여러 메시지를 한 번에 변환할 때 사용하며, 내부적으로 `toUIMessage`를
 * 각 메시지에 적용합니다.
 *
 * @param messages - 백엔드 API로부터 받은 메시지 객체 배열
 * @returns UI용 Message 객체 배열
 *
 * @example
 * // 백엔드 응답 (대화 내역)
 * const backendMessages = [
 *   {
 *     id: 41,
 *     role: 'user',
 *     content: '디지털뱅킹 보고서 작성해줘',
 *     created_at: '2025-01-15T10:29:50Z'
 *   },
 *   {
 *     id: 42,
 *     role: 'assistant',
 *     content: '보고서를 생성했습니다.',
 *     created_at: '2025-01-15T10:30:00Z'
 *   }
 * ]
 *
 * const uiMessages = toUIMessages(backendMessages)
 * // [
 * //   { id: '41', messageId: 41, type: 'user', ... },
 * //   { id: '42', messageId: 42, type: 'assistant', ... }
 * // ]
 *
 * @example
 * // 빈 배열 처리
 * const empty = toUIMessages([])
 * // []
 *
 * @remarks
 * - 배열의 순서는 유지됨
 * - 빈 배열을 전달하면 빈 배열 반환
 * - 각 메시지는 독립적으로 변환됨
 */
export const toUIMessages = (messages: any[]): Message[] => {
    return messages.map(toUIMessage)
}
