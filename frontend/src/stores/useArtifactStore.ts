import {create} from 'zustand'
import {artifactApi} from '../services/artifactApi'
import type {Artifact, ArtifactKind} from '../types/artifact'

/**
 * useArtifactStore.ts
 *
 * 아티팩트(보고서) 캐싱 및 관리
 */

// Re-export for convenience
export type {Artifact, ArtifactKind}

interface ArtifactStore {
    // State - 토픽별 아티팩트 캐시
    artifactsByTopic: Record<number, Artifact[]>

    // State - 로딩 상태 (토픽별)
    loadingTopics: Set<number>

    // State - 토픽별 선택된 아티팩트 ID
    selectedArtifactIds: Record<number, number | null>

    // Actions
    loadArtifacts: (topicId: number) => Promise<Artifact[]>
    refreshArtifacts: (topicId: number) => Promise<Artifact[]>
    invalidateCache: (topicId: number) => void
    clearAllCache: () => void

    // Filtering Actions
    getArtifactsByKind: (topicId: number, kind: ArtifactKind) => Artifact[]
    getMarkdownArtifacts: (topicId: number) => Artifact[]

    // Selection Actions
    selectArtifact: (topicId: number, artifactId: number) => void
    getSelectedArtifactId: (topicId: number) => number | null
    autoSelectLatest: (topicId: number, artifacts: Artifact[]) => void
}

export const useArtifactStore = create<ArtifactStore>((set, get) => ({
    // 초기 상태
    artifactsByTopic: {},
    loadingTopics: new Set(),
    selectedArtifactIds: {},

    /**
     * 아티팩트 로드
     * - 캐시가 있으면 즉시 반환
     * - 캐시가 없으면 API 호출 후 저장
     */
    loadArtifacts: async (topicId: number) => {
        const state = get()

        // 이미 로딩 중이면 대기
        if (state.loadingTopics.has(topicId)) {
            return state.artifactsByTopic[topicId] || []
        }

        // 캐시에 있으면 즉시 반환
        if (state.artifactsByTopic[topicId]) {
            return state.artifactsByTopic[topicId]
        }

        // 로딩 시작
        set((state) => ({
            loadingTopics: new Set(state.loadingTopics).add(topicId)
        }))

        try {
            // API 호출
            const response = await artifactApi.listArtifactsByTopic(topicId)
            const artifacts = response.artifacts

            // 캐시에 저장
            set((state) => {
                const newLoadingTopics = new Set(state.loadingTopics)
                newLoadingTopics.delete(topicId)

                return {
                    artifactsByTopic: {
                        ...state.artifactsByTopic,
                        [topicId]: artifacts
                    },
                    loadingTopics: newLoadingTopics
                }
            })

            return artifacts
        } catch (error) {
            console.error('Failed to load artifacts:', error)

            // 로딩 상태 제거
            set((state) => {
                const newLoadingTopics = new Set(state.loadingTopics)
                newLoadingTopics.delete(topicId)
                return {loadingTopics: newLoadingTopics}
            })

            throw error
        }
    },

    /**
     * 아티팩트 강제 새로고침
     * - 캐시를 무시하고 항상 API 호출
     * - 최신 데이터를 가져와 캐시 업데이트
     */
    refreshArtifacts: async (topicId: number) => {
        const state = get()

        // 이미 로딩 중이면 대기
        if (state.loadingTopics.has(topicId)) {
            return state.artifactsByTopic[topicId] || []
        }

        // 로딩 시작
        set((state) => ({
            loadingTopics: new Set(state.loadingTopics).add(topicId)
        }))

        try {
            // API 호출 (캐시 무시)
            const response = await artifactApi.listArtifactsByTopic(topicId)
            const artifacts = response.artifacts

            // 캐시에 저장
            set((state) => {
                const newLoadingTopics = new Set(state.loadingTopics)
                newLoadingTopics.delete(topicId)

                return {
                    artifactsByTopic: {
                        ...state.artifactsByTopic,
                        [topicId]: artifacts
                    },
                    loadingTopics: newLoadingTopics
                }
            })

            return artifacts
        } catch (error) {
            console.error('Failed to refresh artifacts:', error)

            // 로딩 상태 제거
            set((state) => {
                const newLoadingTopics = new Set(state.loadingTopics)
                newLoadingTopics.delete(topicId)
                return {loadingTopics: newLoadingTopics}
            })

            throw error
        }
    },

    /**
     * 캐시 무효화 (메시지 추가 시 호출)
     * - 해당 토픽의 캐시만 삭제
     */
    invalidateCache: (topicId: number) => {
        set((state) => {
            const newCache = {...state.artifactsByTopic}
            delete newCache[topicId]
            return {artifactsByTopic: newCache}
        })
    },

    /**
     * 전체 캐시 초기화
     */
    clearAllCache: () => {
        set({artifactsByTopic: {}, loadingTopics: new Set(), selectedArtifactIds: {}})
    },

    /**
     * 특정 kind의 아티팩트만 필터링하여 반환
     * @param topicId - 토픽 ID
     * @param kind - 아티팩트 타입 ('md', 'hwpx', 'pdf')
     * @returns 필터링된 아티팩트 배열 (캐시가 없으면 빈 배열 반환)
     */
    getArtifactsByKind: (topicId: number, kind: ArtifactKind) => {
        const state = get()
        const artifacts = state.artifactsByTopic[topicId] || []
        return artifacts.filter((artifact) => artifact.kind === kind)
    },

    /**
     * Markdown 아티팩트만 필터링하여 반환 (getArtifactsByKind의 편의 메서드)
     * @param topicId - 토픽 ID
     * @returns Markdown 아티팩트 배열
     */
    getMarkdownArtifacts: (topicId: number) => {
        return get().getArtifactsByKind(topicId, 'md')
    },

    /**
     * 아티팩트 선택
     */
    selectArtifact: (topicId: number, artifactId: number) => {
        set((state) => ({
            selectedArtifactIds: {
                ...state.selectedArtifactIds,
                [topicId]: artifactId
            }
        }))
    },

    /**
     * 선택된 아티팩트 ID 조회
     */
    getSelectedArtifactId: (topicId: number) => {
        const state = get()
        return state.selectedArtifactIds[topicId] ?? null
    },

    /**
     * 최신 아티팩트 자동 선택 (첫 번째 아이템)
     * 백엔드에서 ORDER BY created_at DESC로 정렬되므로 첫 번째가 최신
     */
    autoSelectLatest: (topicId: number, artifacts: Artifact[]) => {
        if (artifacts.length > 0) {
            // 첫 번째 아티팩트 선택 (가장 최근 생성된 것)
            const latestArtifact = artifacts[0]
            set((state) => ({
                selectedArtifactIds: {
                    ...state.selectedArtifactIds,
                    [topicId]: latestArtifact.id
                }
            }))
        }
    }
}))
