import {useState, useEffect} from 'react'
import {message as antdMessage} from 'antd'
import {messageApi} from '../services/messageApi'
import {artifactApi} from '../services/artifactApi'
import {toUIMessages, enrichMessagesWithArtifacts, type Message} from '../utils/messageHelpers'

/**
 * useMessages.ts
 *
 * 메시지 조회 커스텀 훅
 */

export const useMessages = (selectedTopicId: number | null) => {
    const [messages, setMessages] = useState<Message[]>([])
    const [isLoadingMessages, setIsLoadingMessages] = useState(false)

    /**
     * 특정 주제의 메시지 리스트 조회 (아티팩트 포함)
     */
    const fetchMessages = async (topicId: number) => {
        setIsLoadingMessages(true)
        try {
            // 메시지 리스트 조회
            const messagesResponse = await messageApi.listMessages(topicId)
            const uiMessages = toUIMessages(messagesResponse.messages)

            // 아티팩트 리스트 불러오기
            try {
                const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId)

                // 아티팩트가 있으면 메시지에 연결
                if (artifactsResponse.artifacts.length > 0) {
                    const messagesWithArtifacts = await enrichMessagesWithArtifacts(uiMessages, artifactsResponse.artifacts)
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
     * 메시지 리스트 재조회 (AI 응답 후)
     */
    const refreshMessages = async (topicId: number) => {
        try {
            const messagesResponse = await messageApi.listMessages(topicId)
            const uiMessages = toUIMessages(messagesResponse.messages)

            // 아티팩트 강제 갱신
            const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId)

            if (artifactsResponse.artifacts.length > 0) {
                const messagesWithArtifacts = await enrichMessagesWithArtifacts(uiMessages, artifactsResponse.artifacts)
                setMessages(messagesWithArtifacts)
            } else {
                setMessages(uiMessages)
            }
        } catch (error) {
            console.error('Failed to reload messages:', error)
            antdMessage.error('메시지를 불러오는데 실패했습니다.')
            throw error
        }
    }

    /**
     * 선택된 주제가 변경되면 메시지 자동 조회
     */
    useEffect(() => {
        if (selectedTopicId) {
            fetchMessages(selectedTopicId)
        } else {
            setMessages([])
            setIsLoadingMessages(false)
        }
    }, [selectedTopicId])

    return {
        messages,
        setMessages,
        isLoadingMessages,
        fetchMessages,
        refreshMessages
    }
}
