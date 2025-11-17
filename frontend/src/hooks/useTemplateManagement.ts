import {useState, useEffect, useCallback} from 'react'
import {message} from 'antd'
import {templateApi} from '../services/templateApi'
import type {TemplateListItem, AdminTemplateItem} from '../types/template'

/**
 * useTemplateManagement.ts
 *
 * 템플릿 관리 커스텀 훅
 * - 템플릿 목록 조회, 삭제, 상세 모달 관리 로직
 * - TemplateManagementPage와 AdminTemplateManagement에서 공통으로 사용
 */

interface UseTemplateManagementOptions {
    /** true: 관리자용 (전체 템플릿), false: 사용자용 (내 템플릿) */
    isAdmin?: boolean
}

export const useTemplateManagement = <T extends TemplateListItem | AdminTemplateItem>(options: UseTemplateManagementOptions = {}) => {
    const {isAdmin = false} = options

    // 상태 관리
    const [templates, setTemplates] = useState<T[]>([])
    const [loading, setLoading] = useState(false)
    const [deleting, setDeleting] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [detailModalOpen, setDetailModalOpen] = useState(false)
    const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null)

    /**
     * 템플릿 목록 로드
     * - 관리자: 전체 사용자의 템플릿
     * - 일반 사용자: 내 템플릿
     */
    const loadTemplates = useCallback(async () => {
        setLoading(true)
        try {
            const data = isAdmin ? await templateApi.listAllTemplates() : await templateApi.listTemplates()
            setTemplates(data as T[])
        } catch (error: any) {
            message.error('템플릿 목록을 불러오는데 실패했습니다.')
        } finally {
            setLoading(false)
        }
    }, [isAdmin])

    /**
     * 초기 로드
     */
    useEffect(() => {
        loadTemplates()
    }, [loadTemplates])

    /**
     * 템플릿 상세 모달 열기
     */
    const handleViewDetail = useCallback((templateId: number) => {
        setSelectedTemplateId(templateId)
        setDetailModalOpen(true)
    }, [])

    /**
     * 템플릿 상세 모달 닫기
     */
    const handleCloseDetail = useCallback(() => {
        setDetailModalOpen(false)
        setSelectedTemplateId(null)
    }, [])

    /**
     * 템플릿 삭제
     * - 삭제 후 목록 새로고침
     * - 상세 모달이 열려있으면 닫기
     */
    const handleDelete = useCallback(
        async (templateId: number) => {
            setDeleting(true)
            try {
                await templateApi.deleteTemplate(templateId)
                message.success('템플릿이 삭제되었습니다.')

                // 상세 모달이 열려있으면 닫기
                if (detailModalOpen && selectedTemplateId === templateId) {
                    handleCloseDetail()
                }

                // 목록 새로고침
                await loadTemplates()
            } catch (error: any) {
                message.error('템플릿 삭제에 실패했습니다.')
            } finally {
                setDeleting(false)
            }
        },
        [detailModalOpen, selectedTemplateId, loadTemplates, handleCloseDetail]
    )

    /**
     * 템플릿 업로드
     * - 업로드 후 목록 새로고침
     *
     * @param file - 업로드할 HWPX 파일
     * @param title - 템플릿 제목
     * @returns 업로드 성공 여부
     */
    const handleUpload = useCallback(
        async (file: File, title: string): Promise<boolean> => {
            setUploading(true)
            try {
                await templateApi.uploadTemplate(file, title)
                message.success('템플릿이 업로드되었습니다.')

                // 목록 새로고침
                await loadTemplates()
                return true
            } catch (error: any) {
                message.error('템플릿 업로드에 실패했습니다.')
                return false
            } finally {
                setUploading(false)
            }
        },
        [loadTemplates]
    )

    return {
        // 상태
        templates,
        loading,
        deleting,
        uploading,
        detailModalOpen,
        selectedTemplateId,

        // 액션
        loadTemplates,
        handleViewDetail,
        handleCloseDetail,
        handleDelete,
        handleUpload
    }
}
