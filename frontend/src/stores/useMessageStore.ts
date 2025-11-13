import {create} from 'zustand'
import {message as antdMessage} from 'antd'
import {messageApi} from '../services/messageApi'
import {artifactApi} from '../services/artifactApi'
import {mapMessageResponsesToModels, mapMessageModelsToUI} from '../mapper/messageMapper'
import {enrichMessagesWithArtifacts} from '../utils/messageHelpers'
import type {MessageModel} from '../models/MessageModel'
import type {MessageUI} from '../models/ui/MessageUI'

/**
 * useMessageStore.ts
 *
 * 메시지 관련 상태 관리 (전역)
 * - 메시지 데이터 (topicId별)
 * - UI 상태 (생성/삭제 중)
 * - API 호출 로직 (fetchMessages, refreshMessages)
 */

interface MessageStore {
    // 메시지 데이터 (topicId별로 관리)
    messagesByTopic: Map<number, MessageModel[]>

    // UI 상태
    isGeneratingMessage: boolean
    isDeletingMessage: boolean
    isLoadingMessages: boolean

    // 메시지 데이터 Actions
    setMessages: (topicId: number, messages: MessageModel[]) => void
    addMessages: (topicId: number, messages: MessageModel[]) => void
    clearMessages: (topicId: number) => void
    getMessages: (topicId: number) => MessageModel[]
    getMessagesUI: (topicId: number) => MessageUI[]

    // UI 상태 Actions
    setIsGeneratingMessage: (generating: boolean) => void
    setIsDeletingMessage: (deleting: boolean) => void
    setIsLoadingMessages: (loading: boolean) => void

    // API Actions
    fetchMessages: (topicId: number) => Promise<void>
    refreshMessages: (topicId: number) => Promise<void>
}

export const useMessageStore = create<MessageStore>((set, get) => {
    // 개발 환경에서 MSW가 접근할 수 있도록 window 객체에 노출
    if (typeof window !== 'undefined') {
        // @ts-ignore
        window.__messageStore = {getState: get}
    }

    return {
        // 초기 상태
        messagesByTopic: new Map(),
        isGeneratingMessage: false,
        isDeletingMessage: false,
        isLoadingMessages: false,

        // 메시지 데이터 Actions
        setMessages: (topicId, messages) =>
            set((state) => {
                const newMap = new Map(state.messagesByTopic)
                newMap.set(topicId, messages)
                return {messagesByTopic: newMap}
            }),

        addMessages: (topicId, newMessages) =>
            set((state) => {
                const newMap = new Map(state.messagesByTopic)
                const existing = newMap.get(topicId) || []
                newMap.set(topicId, [...existing, ...newMessages])
                return {messagesByTopic: newMap}
            }),

        clearMessages: (topicId) =>
            set((state) => {
                const newMap = new Map(state.messagesByTopic)
                newMap.delete(topicId)
                return {messagesByTopic: newMap}
            }),

        getMessages: (topicId) => {
            const state = get()
            return state.messagesByTopic.get(topicId) || []
        },

        getMessagesUI: (topicId) => {
            const messages = get().messagesByTopic.get(topicId) || []
            return mapMessageModelsToUI(messages)
        },

        // UI 상태 Actions
        setIsGeneratingMessage: (generating) => set({isGeneratingMessage: generating}),
        setIsDeletingMessage: (deleting) => set({isDeletingMessage: deleting}),
        setIsLoadingMessages: (loading) => set({isLoadingMessages: loading}),

        // API Actions
        /**
         * 특정 주제의 메시지 리스트 조회 (아티팩트 포함)
         * - 실제 topicId에 대해 백엔드에서 메시지 조회
         * - 임시 topicId(-1)의 메시지와 병합하지 않음 (MSW가 처리)
         */
        fetchMessages: async (topicId: number) => {
            set({isLoadingMessages: true})
            try {
                // ✅ 임시 topicId(음수)인 경우 백엔드 호출하지 않음
                if (topicId < 0) {
                    // 이미 addOutlineMessage로 저장된 메시지 사용
                    set({isLoadingMessages: false})
                    return
                }

                // 1. 메시지 리스트 조회
                const messagesResponse = await messageApi.listMessages(topicId)

                // 2. Response → Model 변환
                const messageModels = mapMessageResponsesToModels(messagesResponse.messages)

                // 3. 아티팩트 리스트 불러오기
                try {
                    const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId)

                    // 4. 아티팩트가 있으면 메시지에 연결
                    if (artifactsResponse.artifacts.length > 0) {
                        const messagesWithArtifacts = await enrichMessagesWithArtifacts(messageModels, artifactsResponse.artifacts)
                        get().setMessages(topicId, messagesWithArtifacts)
                    } else {
                        get().setMessages(topicId, messageModels)
                    }
                } catch (error) {
                    console.error('Failed to load artifacts:', error)
                    // 아티팩트 로드 실패 시에도 메시지는 표시
                    get().setMessages(topicId, messageModels)
                }
            } catch (error: any) {
                console.error('Failed to load messages:', error)
                antdMessage.error('메시지를 불러오는데 실패했습니다.')
            } finally {
                set({isLoadingMessages: false})
            }
        },

        /**
         * 메시지 리스트 재조회 (AI 응답 후)
         */
        refreshMessages: async (topicId: number) => {
            try {
                // 1. 메시지 리스트 조회
                const messagesResponse = await messageApi.listMessages(topicId)

                // 2. Response → Model 변환
                const messageModels = mapMessageResponsesToModels(messagesResponse.messages)

                // 3. 아티팩트 강제 갱신
                const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId)

                if (artifactsResponse.artifacts.length > 0) {
                    const messagesWithArtifacts = await enrichMessagesWithArtifacts(messageModels, artifactsResponse.artifacts)
                    get().setMessages(topicId, messagesWithArtifacts)
                } else {
                    get().setMessages(topicId, messageModels)
                }
            } catch (error) {
                console.error('Failed to reload messages:', error)
                antdMessage.error('메시지를 불러오는데 실패했습니다.')
                throw error
            }
        }
    }
})
