/**
 * messageHelpers.ts
 * 
 * 메시지 관련 유틸리티 함수
 * - 메시지와 아티팩트 연결
 * - 메시지 변환 함수
 */

import {artifactApi} from '../services/artifactApi'
import type {Artifact} from '../types/artifact'

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
 * 단일 메시지에 아티팩트 내용 연결
 */
export const enrichMessageWithArtifact = async (
    msg: Message,
    artifacts: Artifact[]
): Promise<Message> => {
    // 이 메시지와 연결된 MD 아티팩트 찾기
    const relatedArtifact = artifacts.find(
        (art) => art.kind === 'md' && art.message_id === msg.messageId
    )

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
 * 여러 메시지에 아티팩트 내용 일괄 연결
 */
export const enrichMessagesWithArtifacts = async (
    messages: Message[],
    artifacts: Artifact[]
): Promise<Message[]> => {
    return Promise.all(
        messages.map((msg) => enrichMessageWithArtifact(msg, artifacts))
    )
}

/**
 * 백엔드 메시지를 UI 메시지 형식으로 변환
 */
export const toUIMessage = (msg: any): Message => ({
    id: msg.id.toString(),
    messageId: msg.id,
    type: msg.role === 'user' ? 'user' : 'assistant',
    content: msg.content,
    timestamp: new Date(msg.created_at)
})

/**
 * 백엔드 메시지 배열을 UI 메시지 배열로 변환
 */
export const toUIMessages = (messages: any[]): Message[] => {
    return messages.map(toUIMessage)
}
