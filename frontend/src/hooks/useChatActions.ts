import {message as antdMessage} from 'antd'
import {topicApi} from '../services/topicApi'
import {useTopicStore} from '../stores/useTopicStore'
import {useArtifactStore} from '../stores/useArtifactStore'
import type {Message} from '../utils/messageHelpers'
import type { Artifact } from '../types/artifact'

/**
 * useChatActions.ts
 * 
 * 채팅 메시지 전송 및 토픽 관리 커스텀 훅
 */

interface UseChatActionsOptions {
    selectedTopicId: number | null
    setSelectedTopicId: (id: number | null) => void
    setMessages: (messages: Message[] | ((prev: Message[]) => Message[])) => void
    setIsGenerating: (generating: boolean) => void
    reloadMessagesWithArtifacts: (topicId: number) => Promise<void>
}

export const useChatActions = ({
    selectedTopicId,
    setSelectedTopicId,
    setMessages,
    setIsGenerating,
    reloadMessagesWithArtifacts
}: UseChatActionsOptions) => {
    const {addTopic} = useTopicStore()
    const {loadArtifacts, autoSelectLatest, getSelectedArtifactId, refreshArtifacts} = useArtifactStore()

    /**
     * 메시지 전송 핸들러
     */
    const handleSendMessage = async (
        message: string,
        files: File[],
        webSearchEnabled: boolean
    ) => {
        // 사용자 메시지 임시 추가
        const tempUserMessage: Message = {
            id: 'temp-' + Date.now(),
            messageId: 0,
            type: 'user',
            content: message,
            timestamp: new Date()
        }

        // 새 대화인 경우 이전 메시지를 무시하고 새로 시작
        if (selectedTopicId === null) {
            setMessages([tempUserMessage])
        } else {
            setMessages((prev) => [...prev, tempUserMessage])
        }
        
        setIsGenerating(true)

        try {
            let currentTopicId = selectedTopicId

            // 첫 메시지: 토픽 생성 + AI 보고서 자동 생성
            if (currentTopicId === null) {
                const generateResponse = await topicApi.generateTopic({
                    input_prompt: message,
                    language: 'ko'
                })
                currentTopicId = generateResponse.topic_id

                // Fetch the complete topic data and add to store
                try {
                    const newTopic = await topicApi.getTopic(currentTopicId)
                    addTopic(newTopic)
                } catch (error) {
                    console.error('Failed to fetch topic after creation:', error)
                }
            } else {
                // 2번째 메시지부터: 메시지 체이닝 (ask API)
                let selectedArtifactId = getSelectedArtifactId(currentTopicId)

                // 참조 보고서 선택: 선택된 아티팩트가 없으면 자동으로 최신 선택 (MD 파일만)
                if (!selectedArtifactId) {
                    const artifacts = await loadArtifacts(currentTopicId)
                    const markdownArtifacts = artifacts.filter((art) => art.kind === 'md')
                    if (markdownArtifacts.length > 0) {
                        autoSelectLatest(currentTopicId, markdownArtifacts)
                        selectedArtifactId = getSelectedArtifactId(currentTopicId)
                    }
                }

                await topicApi.askTopic(currentTopicId, {
                    content: message,
                    artifact_id: selectedArtifactId,
                    include_artifact_content: true
                })
            }

            // 메시지 목록 재조회 (AI 응답 포함)
            await reloadMessagesWithArtifacts(currentTopicId)

            // Artifact 캐시 갱신 (새로운 MD 파일이 생성되었을 수 있음)
            const refreshedArtifacts: Artifact[] = await refreshArtifacts(currentTopicId)

            // 새로운 MD 파일이 생성되므로 참조 보고서를 최신 MD 파일로 선택
            autoSelectLatest(currentTopicId, refreshedArtifacts)

            // 메시지 로드 완료료 후 selectedTopicId 업데이트 (useEffect 중복 실행 방지)
            if (selectedTopicId !== currentTopicId) {
                setSelectedTopicId(currentTopicId)
            }
        } catch (error: any) {
            console.error('Error sending message:', error)
            antdMessage.error('메시지 전송에 실패했습니다.')

            // 에러 메시지 추가
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                messageId: 0,
                type: 'assistant',
                content: '메시지 전송 중 오류가 발생했습니다. 다시 시도해주세요.',
                timestamp: new Date()
            }
            setMessages((prev) => [...prev, errorMessage])
        } finally {
            setIsGenerating(false)
        }
    }

    return {
        handleSendMessage
    }
}
