import {useState, useEffect} from 'react'
import {message as antdMessage} from 'antd'
import {messageApi} from '../services/messageApi'
import {artifactApi} from '../services/artifactApi'
import {
    toUIMessages,
    enrichMessagesWithArtifacts,
    type Message
} from '../utils/messageHelpers'

/**
 * useMessages.ts
 * 
 * 메시지 상태 및 로딩 관리 커스텀 훅
 */

export const useMessages = (selectedTopicId: number | null) => {
    const [messages, setMessages] = useState<Message[]>([])
    const [isLoadingMessages, setIsLoadingMessages] = useState(false)
    const [isGenerating, setIsGenerating] = useState(false)

    /**
     * 선택된 토픽의 메시지 로드 (아티팩트 포함)
     */
    const loadTopicMessages = async (topicId: number) => {
        setIsLoadingMessages(true)
        try {
            // 메시지 목록 조회
            const messagesResponse = await messageApi.listMessages(topicId)
            const uiMessages = toUIMessages(messagesResponse.messages)

            // 아티팩트 목록 불러오기
            try {
                const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId)

                // 아티팩트가 있으면 메시지에 연결
                if (artifactsResponse.artifacts.length > 0) {
                    const messagesWithArtifacts = await enrichMessagesWithArtifacts(
                        uiMessages,
                        artifactsResponse.artifacts
                    )
                    setMessages(messagesWithArtifacts)
                } else {
                    setMessages(uiMessages)
                }
            } catch (error) {
                console.error('Failed to load artifacts:', error)
                // 아티팩트 로드 실패 시에도 메시지는 표시
                setMessages(uiMessages)
            }
        } catch (error: any) {
            console.error('Failed to load messages:', error)
            antdMessage.error('메시지를 불러오는데 실패했습니다.')
        } finally {
            setIsLoadingMessages(false)
        }
    }

    /**
     * 메시지 목록 재조회 (AI 응답 후)
     */
    const reloadMessagesWithArtifacts = async (topicId: number) => {
        try {
            const messagesResponse = await messageApi.listMessages(topicId)
            const uiMessages = toUIMessages(messagesResponse.messages)

            // 아티팩트 강제 갱신
            const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId)

            if (artifactsResponse.artifacts.length > 0) {
                const messagesWithArtifacts = await enrichMessagesWithArtifacts(
                    uiMessages,
                    artifactsResponse.artifacts
                )
                setMessages(messagesWithArtifacts)
            } else {
                setMessages(uiMessages)
            }
        } catch (error) {
            console.error('Failed to reload messages:', error)
            throw error
        }
    }

    /**
     * 선택된 토픽이 변경되면 메시지 자동 로드
     */
    useEffect(() => {
        if (selectedTopicId) {
            loadTopicMessages(selectedTopicId)
        } else {
            setMessages([])
            setIsLoadingMessages(false)
        }
    }, [selectedTopicId])

    return {
        messages,
        setMessages,
        isLoadingMessages,
        isGenerating,
        setIsGenerating,
        loadTopicMessages,
        reloadMessagesWithArtifacts
    }
}
