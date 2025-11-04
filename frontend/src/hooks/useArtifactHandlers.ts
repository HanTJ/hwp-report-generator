import {useState} from 'react'
import {message as antdMessage} from 'antd'
import {artifactApi} from '../services/artifactApi'
import {useArtifactStore, type Artifact} from '../stores/useArtifactStore'

/**
 * useArtifactHandlers.ts
 * 
 * 아티팩트 관련 핸들러 및 상태 관리 커스텀 훅
 */

interface UseArtifactHandlersReturn {
    // Dropdown 상태
    isReportsDropdownOpen: boolean
    setIsReportsDropdownOpen: (isOpen: boolean) => void
    
    // Store actions
    loadArtifacts: (topicId: number) => Promise<Artifact[]>             // 아티팩트 목록 불러오기
    refreshArtifacts: (topicId: number) => Promise<Artifact[]>          // 아티팩트 목록 갱신
    getMarkdownArtifacts: (topicId: number) => Artifact[]               // MD 아티팩트 리스트만 반환
    getSelectedArtifactId: (topicId: number) => number | null           // 선택된 아티팩트 ID 반환
    selectArtifact: (topicId: number, artifactId: number) => void       // 아티팩트 선택
    autoSelectLatest: (topicId: number, artifacts: Artifact[]) => void  // MD 아티팩트 중 최신 것을 자동 선택
    loadingTopics: Set<number>                                          // 로딩 중인 토픽 ID 집합 
    
    // Handlers
    handleReportsClick: (topicId: number | null) => Promise<void>                                   // 보고서 버튼 클릭 (Dropdown 열기) 
    handleArtifactSelect: (topicId: number | null, artifactId: number) => void                      // 보고서 선택
    handleArtifactDownload: (artifact: Artifact, topicId: number | null) => Promise<void>           // 보고서 다운로드
    handleArtifactPreview: (artifact: Artifact, onSuccess: (data: any) => void) => Promise<void>    // 보고서 미리보기
}

export const useArtifactHandlers = (): UseArtifactHandlersReturn => {
    const [isReportsDropdownOpen, setIsReportsDropdownOpen] = useState(false)
    
    const {
        loadArtifacts,
        refreshArtifacts,
        getMarkdownArtifacts,
        getSelectedArtifactId,
        selectArtifact,
        autoSelectLatest,
        loadingTopics
    } = useArtifactStore()

    /**
     * 보고서 버튼 클릭 (Dropdown 열기)
     */
    const handleReportsClick = async (topicId: number | null) => {
        if (!topicId) {
            antdMessage.info('새로운 주제를 먼저 입력하세요.')
            return
        }

        setIsReportsDropdownOpen(true)

        try {
            const artifacts = await loadArtifacts(topicId)
            
            console.log('useArtifiactHandlers > loadArtifacts >', artifacts)

            // 아직 선택된 아티팩트가 없으면 자동으로 마지막 선택 (MD 파일만)
            const markdownArtifacts = artifacts.filter((art) => art.kind === 'md')
            if (!getSelectedArtifactId(topicId) && markdownArtifacts.length > 0) {
                autoSelectLatest(topicId, markdownArtifacts)
            }
        } catch (error: any) {
            antdMessage.error('보고서 목록을 불러오는데 실패했습니다.')
            console.error('Failed to load artifacts:', error)
        }
    }

    /**
     * 아티팩트 선택
     */
    const handleArtifactSelect = (topicId: number | null, artifactId: number) => {
        if (topicId) {
            selectArtifact(topicId, artifactId)
        }
    }

    /**
     * 아티팩트 다운로드 (HWPX 변환)
     */
    const handleArtifactDownload = async (artifact: Artifact, topicId: number | null) => {
        try {
            antdMessage.loading({
                content: 'HWPX 파일 다운로드 중...',
                key: 'download',
                duration: 0
            })

            // message_id가 있으면 메시지 기반 HWPX 다운로드 사용
            if (artifact.message_id) {
                const hwpxFilename = artifact.filename.replace('.md', '.hwpx')
                await artifactApi.downloadMessageHwpx(artifact.message_id, hwpxFilename)

                // HWPX 다운로드 후 artifact 목록 갱신 (새로운 hwpx artifact가 생성됨)
                if (topicId) {
                    await refreshArtifacts(topicId)
                }
            } else {
                antdMessage.error('HWPX 파일 다운로드에 실패했습니다.')
                return
            }
            
            antdMessage.destroy('download')
            antdMessage.success('HWPX 파일이 다운로드되었습니다.')
        } catch (error: any) {
            antdMessage.destroy('download')
            antdMessage.error('HWPX 파일 다운로드에 실패했습니다.')
            console.error('Download failed:', error)
        }
    }

    /**
     * 아티팩트 미리보기
     */
    const handleArtifactPreview = async (
        artifact: Artifact,
        onSuccess: (data: any) => void
    ) => {
        try {
            const contentResponse = await artifactApi.getArtifactContent(artifact.id)
            
            onSuccess({
                filename: artifact.filename,
                content: contentResponse.content,
                messageId: artifact.message_id,
                reportId: artifact.id
            })
            
            setIsReportsDropdownOpen(false)
        } catch (error: any) {
            antdMessage.error('미리보기를 불러오는데 실패했습니다.')
            console.error('Failed to preview artifact:', error)
        }
    }

    return {
        isReportsDropdownOpen,
        setIsReportsDropdownOpen,
        loadArtifacts,
        refreshArtifacts,
        getMarkdownArtifacts,
        getSelectedArtifactId,
        selectArtifact,
        autoSelectLatest,
        loadingTopics,
        handleReportsClick,
        handleArtifactSelect,
        handleArtifactDownload,
        handleArtifactPreview
    }
}
