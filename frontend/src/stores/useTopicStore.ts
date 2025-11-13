import {create} from 'zustand'
import {message as antdMessage} from 'antd'
import {topicApi} from '../services/topicApi'
import type {Topic, TopicUpdate, PlanResponse} from '../types/topic'
import type {MessageModel} from '../models/MessageModel'
import {UI_CONFIG} from '../constants'

/**
 * useTopicStore.ts
 *
 * 토픽 관리
 */

interface TopicStore {
    // State - Sidebar용 (항상 첫 페이지만 표시)
    sidebarTopics: Topic[]
    sidebarLoading: boolean

    // State - TopicListPage용 (페이지네이션)
    pageTopics: Topic[]
    pageLoading: boolean
    pageTotalTopics: number
    pageCurrentPage: number
    pagePageSize: number

    // State - 공통
    selectedTopicId: number | null
    tempTopicIdCounter: number // 임시 topicId 카운터 (음수)

    // State - 계획 생성
    plan: PlanResponse | null
    planLoading: boolean
    planError: string | null

    // Actions - Sidebar용
    loadSidebarTopics: () => Promise<void>

    // Actions - TopicListPage용
    loadPageTopics: (page: number, pageSize: number) => Promise<void>

    // Actions - 공통 (양쪽 리스트에 모두 반영)
    addTopic: (topic: Topic) => void
    updateTopicInBothLists: (topicId: number, updates: Partial<Topic>) => void
    removeTopicFromBothLists: (topicId: number) => Promise<void>
    setSelectedTopicId: (id: number | null) => void
    createTempTopicId: () => number // 임시 topicId 생성
    resetTempCounter: () => void // 임시 카운터 초기화
    refreshTopic: (topicId: number) => Promise<void>
    updateTopicById: (topicId: number, data: TopicUpdate) => Promise<void>
    deleteTopicById: (topicId: number) => Promise<void>

    // Actions - 계획 생성
    generatePlan: (templateId: number, topic: string) => Promise<void>
    handleTopicPlanWithMessages: (
        templateId: number,
        userMessage: string,
        addMessages: (topicId: number, messages: MessageModel[]) => void
    ) => Promise<void>
    clearPlan: () => void
}

export const useTopicStore = create<TopicStore>((set, get) => ({
    // 초기 상태 - Sidebar용
    sidebarTopics: [],
    sidebarLoading: false,

    // 초기 상태 - TopicListPage용
    pageTopics: [],
    pageLoading: false,
    pageTotalTopics: 0,
    pageCurrentPage: 1,
    pagePageSize: 20,

    // 초기 상태 - 공통
    selectedTopicId: null,
    tempTopicIdCounter: 0,

    // 초기 상태 - 계획 생성
    plan: null,
    planLoading: false,
    planError: null,

    // Sidebar용 토픽 로드 (항상 첫 페이지만)
    loadSidebarTopics: async () => {
        set({sidebarLoading: true})
        try {
            const response = await topicApi.listTopics('active', 1, UI_CONFIG.PAGINATION.SIDEBAR_TOPICS_PER_PAGE)

            set({
                sidebarTopics: response.topics,
                sidebarLoading: false
            })
        } catch (error) {
            console.error('Failed to load sidebar topics:', error)
            set({sidebarLoading: false})
            throw error
        }
    },

    // TopicListPage용 토픽 로드 (페이지네이션)
    loadPageTopics: async (page, pageSize) => {
        set({pageLoading: true})
        try {
            const response = await topicApi.listTopics('active', page, pageSize)

            set({
                pageTopics: response.topics,
                pageTotalTopics: response.total,
                pageCurrentPage: page,
                pagePageSize: pageSize,
                pageLoading: false
            })
        } catch (error) {
            console.error('Failed to load page topics:', error)
            set({pageLoading: false})
            throw error
        }
    },

    // 토픽 생성 후 양쪽 리스트에 추가
    addTopic: (topic) => {
        set((state) => {
            // Sidebar: 최신 토픽을 앞에 추가하고, SIDEBAR_TOPICS_PER_PAGE 제한 적용
            const newSidebarTopics = [topic, ...state.sidebarTopics].slice(0, UI_CONFIG.PAGINATION.SIDEBAR_TOPICS_PER_PAGE)

            // Page: 제한 없이 추가 (페이지네이션은 loadPageTopics에서 관리)
            const newPageTopics = [topic, ...state.pageTopics]

            return {
                sidebarTopics: newSidebarTopics,
                pageTopics: newPageTopics
            }
        })
    },

    // 토픽 업데이트 (양쪽 리스트에 모두 반영)
    updateTopicInBothLists: (topicId, updates) => {
        set((state) => ({
            sidebarTopics: state.sidebarTopics.map((topic) => (topic.id === topicId ? {...topic, ...updates} : topic)),
            pageTopics: state.pageTopics.map((topic) => (topic.id === topicId ? {...topic, ...updates} : topic))
        }))
    },

    // 양쪽 리스트에서 토픽 삭제
    removeTopicFromBothLists: async (topicId) => {
        set((state) => ({
            sidebarTopics: state.sidebarTopics.filter((topic) => topic.id !== topicId),
            pageTopics: state.pageTopics.filter((topic) => topic.id !== topicId),
            selectedTopicId: state.selectedTopicId === topicId ? null : state.selectedTopicId
        }))

        // 사이드바 토픽 재로드 (삭제 후 빈 자리를 채우기 위해)
        try {
            await get().loadSidebarTopics()
        } catch (error) {
            console.error('Failed to reload sidebar topics after deletion:', error)
        }
    },

    // 선택된 토픽 ID 설정
    setSelectedTopicId: (id) => {
        set({selectedTopicId: id})
    },

    // 임시 topicId 생성 (음수)
    createTempTopicId: () => {
        const state = get()
        const tempId = state.tempTopicIdCounter - 1
        set({tempTopicIdCounter: tempId})
        return tempId
    },

    // 임시 카운터 초기화
    resetTempCounter: () => {
        set({tempTopicIdCounter: 0})
    },

    // 특정 토픽 조회 (API 호출 + 양쪽 상태 업데이트)
    refreshTopic: async (topicId) => {
        try {
            const updatedTopic = await topicApi.getTopic(topicId)
            get().updateTopicInBothLists(topicId, updatedTopic)
        } catch (error) {
            console.error('Failed to refresh topic:', error)
            throw error
        }
    },

    // 특정 토픽 수정 (API 호출 + 양쪽 상태 업데이트)
    updateTopicById: async (topicId, data) => {
        try {
            const updatedTopic = await topicApi.updateTopic(topicId, data)
            get().updateTopicInBothLists(topicId, updatedTopic)
        } catch (error) {
            console.error('Failed to update topic:', error)
            throw error
        }
    },

    // 토픽 삭제 (API 호출 + 양쪽 스토어에서 삭제)
    deleteTopicById: async (topicId) => {
        try {
            await topicApi.deleteTopic(topicId)
            get().removeTopicFromBothLists(topicId)
        } catch (error) {
            console.error('Failed to delete topic:', error)
            throw error
        }
    },

    // 보고서 작성 계획 생성
    generatePlan: async (templateId, topic) => {
        set({planLoading: true, planError: null})
        try {
            const result = await topicApi.generateTopicPlan({
                template_id: templateId,
                topic: topic
            })

            set({
                plan: result,
                planLoading: false,
                planError: null
            })
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : '계획 생성에 실패했습니다.'
            console.error('Failed to generate plan:', error)
            set({
                plan: null,
                planLoading: false,
                planError: errorMessage
            })
            throw error
        }
    },

    // 보고서 계획 요청 + 메시지 관리
    handleTopicPlanWithMessages: async (templateId, userMessage, addMessages) => {
        if (!userMessage.trim()) {
            antdMessage.warning('메시지를 입력해주세요.')
            return
        }

        const tempTopicId = 0 // 임시 topicId 고정
        const seqNo = 1 // 첫 번째 메시지이므로 고정

        // 1. 사용자 메시지를 UI에 표시
        const userMsgModel: MessageModel = {
            id: undefined,
            topicId: tempTopicId,
            role: 'user',
            content: userMessage.trim(),
            seqNo: seqNo,
            createdAt: new Date().toISOString()
        }

        // 2. 사용자 메시지 상태에 추가
        addMessages(tempTopicId, [userMsgModel])

        try {
            // 3. 계획 생성 API 호출
            await get().generatePlan(templateId, userMessage.trim())

            // 4. plan 상태에서 결과 가져와서 메시지로 추가
            const currentPlan = get().plan
            if (currentPlan) {
                const assistantMsgModel: MessageModel = {
                    id: undefined,
                    topicId: currentPlan.topic_id,
                    role: 'assistant',
                    content: currentPlan.plan,
                    seqNo: seqNo + 1,
                    createdAt: new Date().toISOString()
                }

                // AI 응답 메시지 상태에 추가
                addMessages(assistantMsgModel.topicId, [assistantMsgModel])
            }
        } catch (error: any) {
            console.error('개요 요청 실패:', error)
            const currentError = get().planError
            antdMessage.error(currentError || '개요 생성에 실패했습니다.')

            // 에러 메시지 추가
            const errorMsgModel: MessageModel = {
                id: undefined,
                topicId: tempTopicId,
                role: 'assistant',
                content: currentError || '보고서 계획 생성에 실패했습니다.',
                seqNo: seqNo + 1,
                createdAt: new Date().toISOString()
            }
            addMessages(tempTopicId, [errorMsgModel])
        }
    },

    // 계획 초기화
    clearPlan: () => {
        set({
            plan: null,
            planLoading: false,
            planError: null
        })
    }
}))
