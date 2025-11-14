import {create} from 'zustand'
import {message as antdMessage} from 'antd'
import {topicApi} from '../services/topicApi'
import {messageApi} from '../services/messageApi'
import {artifactApi} from '../services/artifactApi'
import type {Topic, TopicUpdate, PlanResponse} from '../types/topic'
import type {MessageModel} from '../models/MessageModel'
import {UI_CONFIG} from '../constants'
import {useMessageStore} from './useMessageStore'
import {mapMessageResponsesToModels} from '../mapper/messageMapper'
import {enrichMessagesWithArtifacts} from '../utils/messageHelpers'

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
    refreshTopic: (topicId: number) => Promise<void>
    updateTopicById: (topicId: number, data: TopicUpdate) => Promise<void>
    deleteTopicById: (topicId: number) => Promise<void>
    updateMessagesTopic: (oldTopicId: number, newTopicId: number) => void

    // Actions - 계획 생성
    generatePlan: (templateId: number, topic: string) => Promise<void>
    handleTopicPlanWithMessages: (
        templateId: number,
        userMessage: string,
        addMessages: (topicId: number, messages: MessageModel[]) => void
    ) => Promise<void>
    updatePlan: (newPlan: string) => void
    clearPlan: () => void

    // Actions - 보고서 생성
    generateReportFromPlan: (setIsLoadingMessages: (loading: boolean) => void) => Promise<void>
}

export const useTopicStore = create<TopicStore>((set, get) => {
    // 개발 환경에서 콘솔로 접근할 수 있도록 window 객체에 노출
    if (typeof window !== 'undefined') {
        // @ts-ignore
        window.__topicStore = {getState: get}
    }

    return {
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

        // 토픽과 연관된 메시지들의 topicId 업데이트
        updateMessagesTopic: (oldTopicId: number, newTopicId: number) => {
            const messageStore = useMessageStore.getState()

            // oldTopicId의 메시지 가져오기
            const oldMessages = messageStore.getMessages(oldTopicId)

            if (!oldMessages || oldMessages.length === 0) {
                return
            }

            // topicId 변경한 새 메시지 배열 생성
            const updatedMessages = oldMessages.map((msg) => ({
                ...msg,
                topicId: newTopicId
            }))

            // 기존 임시 메시지 제거
            messageStore.clearMessages(oldTopicId)

            // 새 topicId로 메시지 세팅
            messageStore.setMessages(newTopicId, updatedMessages)
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
            const prevTopicId = get().selectedTopicId

            // 토픽 전환 시 이전 토픽의 계획 모드 메시지(topicId=0) 정리
            if (prevTopicId !== id) {
                const messageStore = useMessageStore.getState()

                // 계획 모드(topicId=0)에서 실제 토픽으로 이동 시 정리
                if (prevTopicId === 0 && id !== null && id !== 0) {
                    messageStore.clearMessages(0)
                    get().clearPlan() // plan 상태도 함께 정리
                }
            }

            set({selectedTopicId: id})
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

            // 1. 사용자 메시지를 UI에 표시
            const userMsgModel: MessageModel = {
                id: undefined,
                topicId: tempTopicId,
                role: 'user',
                content: userMessage.trim(),
                seqNo: undefined,
                createdAt: new Date().toISOString(),
                isPlan: false
            }

            // 2. 사용자 메시지 상태에 추가
            addMessages(tempTopicId, [userMsgModel])

            // 🆕 즉시 selectedTopicId 설정 (사용자 메시지가 바로 보이도록)
            set({selectedTopicId: tempTopicId})

            try {
                // 3. 계획 생성 API 호출
                await get().generatePlan(templateId, userMessage.trim())

                // 4. plan 상태에서 결과 가져와서 메시지로 추가
                const currentPlan = get().plan
                if (currentPlan) {
                    // realTopicId는 나중에 generateReportFromPlan에서 사용됨
                    // 여기서는 계획 메시지를 topicId=0에 저장

                    const assistantMsgModel: MessageModel = {
                        id: undefined,
                        topicId: tempTopicId, // ⚠️ 먼저 tempTopicId=0에 저장
                        role: 'assistant',
                        content: currentPlan.plan,
                        seqNo: undefined,
                        createdAt: new Date().toISOString(),
                        isPlan: true // 계획 메시지 표시
                    }

                    // AI 응답 메시지를 tempTopicId=0에 추가
                    addMessages(tempTopicId, [assistantMsgModel])

                    // selectedTopicId 업데이트 (계획 모드 유지: topicId=0)
                    // ⚠️ 이 시점에는 아직 실제 토픽으로 전환하지 않음
                    // 보고서 생성("예" 버튼) 시에만 realTopicId로 전환
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
                    seqNo: undefined,
                    createdAt: new Date().toISOString(),
                    isPlan: true // 계획 메시지 표시
                }
                addMessages(tempTopicId, [errorMsgModel])
            }
        },

        // 계획 업데이트
        updatePlan: (newPlan) => {
            set((state) => {
                if (!state.plan) return state

                return {
                    plan: {
                        ...state.plan,
                        plan: newPlan
                    }
                }
            })
        },

        // 계획 초기화
        clearPlan: () => {
            set({
                plan: null,
                planLoading: false,
                planError: null
            })
        },

        /**
         * 계획 기반 보고서 생성
         * "예" 클릭 시 호출 - 백그라운드에서 실제 보고서 생성
         */
        generateReportFromPlan: async (setIsLoadingMessages) => {
            const state = get()
            const {plan} = state

            if (!plan) {
                antdMessage.error('계획 정보가 없습니다.')
                return
            }

            const realTopicId = plan.topic_id

            try {
                // ChatInput 비활성화 (새 메시지 전송 방지)
                setIsLoadingMessages(true)

                antdMessage.loading({
                    content: '보고서 생성 요청 중...',
                    key: 'generate',
                    duration: 0
                })

                // 백그라운드 보고서 생성 API 호출 (새로운 API)
                const response = await topicApi.generateTopicBackground(realTopicId, {
                    topic: plan.plan.split('\n')[0].replace('# ', '').replace(' 작성 계획', ''), // 첫 줄에서 주제 추출
                    plan: plan.plan,
                    template_id: 1 // TODO: template_id 저장 필요
                })

                antdMessage.destroy('generate')

                // 202 Accepted - 백그라운드에서 생성 중
                if (response.status === 'generating') {
                    antdMessage.loading({
                        content: '보고서 생성 중... (완료까지 약 10초)',
                        key: 'generating',
                        duration: 0
                    })

                    // 폴링으로 상태 확인 (3초마다, 최대 30초)
                    let attempts = 0
                    const maxAttempts = 10
                    const pollInterval = 3000

                    const checkStatus = async () => {
                        try {
                            const status = await topicApi.getGenerationStatus(realTopicId)

                            if (status.status === 'completed') {
                                antdMessage.destroy('generating')
                                antdMessage.success('보고서가 생성되었습니다.')

                                const messageStore = useMessageStore.getState()

                                // 1. 기존 계획 모드 메시지 (topicId=0) 가져오기
                                const planMessages = messageStore.getMessages(0)

                                // 2. 서버에서 메시지 + Artifact 조회
                                const messagesResponse = await messageApi.listMessages(realTopicId)
                                const messageModels = mapMessageResponsesToModels(messagesResponse.messages)
                                const artifactsResponse = await artifactApi.listArtifactsByTopic(realTopicId)
                                const serverMessages = await enrichMessagesWithArtifacts(messageModels, artifactsResponse.artifacts)

                                // 3. 계획 메시지의 topicId 업데이트 (0 → realTopicId)
                                const updatedPlanMessages = planMessages.map((msg) => ({
                                    ...msg,
                                    topicId: realTopicId
                                }))

                                // 4. 중복 제거: ID 기반으로 중복 체크
                                const planMessageIds = new Set(updatedPlanMessages.filter((m) => m.id).map((m) => m.id))
                                const newServerMessages = serverMessages.filter((m: MessageModel) => {
                                    if (!m.id) return true // ID 없으면 추가
                                    return !planMessageIds.has(m.id) // 중복 체크
                                })

                                // 5. 계획 메시지 + 서버 메시지 병합
                                const mergedMessages = [...updatedPlanMessages, ...newServerMessages]
                                messageStore.setMessages(realTopicId, mergedMessages)

                                // 6. 계획 모드 메시지 정리 (topicId=0 삭제)
                                messageStore.clearMessages(0)

                                // 7. selectedTopicId 전환
                                set({selectedTopicId: realTopicId})

                                setIsLoadingMessages(false)
                            } else if (status.status === 'failed') {
                                antdMessage.destroy('generating')
                                antdMessage.error(status.error_message || '보고서 생성에 실패했습니다.')
                                setIsLoadingMessages(false)
                            } else if (attempts < maxAttempts) {
                                // 계속 진행 중
                                attempts++
                                setTimeout(checkStatus, pollInterval)
                            } else {
                                antdMessage.destroy('generating')
                                antdMessage.warning('보고서 생성이 오래 걸립니다. 잠시 후 다시 확인해주세요.')

                                // 타임아웃이어도 topic으로 전환
                                set({selectedTopicId: realTopicId})
                                setIsLoadingMessages(false)
                            }
                        } catch (error) {
                            console.error('상태 확인 실패:', error)
                            antdMessage.destroy('generating')
                            antdMessage.error('상태 확인에 실패했습니다.')
                            setIsLoadingMessages(false)
                        }
                    }

                    // 첫 상태 확인 시작
                    setTimeout(checkStatus, pollInterval)
                }
            } catch (error: any) {
                console.error('보고서 생성 실패:', error)
                antdMessage.destroy('generate')
                antdMessage.error('보고서 생성에 실패했습니다.')
                setIsLoadingMessages(false)
            }
        }
    }
})
