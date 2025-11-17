/**
 * services/templateApi.ts
 *
 * 템플릿 관련 API 서비스
 */

import api from './api'
import {API_ENDPOINTS} from '../constants'
import type {ApiResponse} from '../types/api'
import type {
    TemplateListItem,
    TemplateDetail,
    UploadTemplateResponse,
    DeleteTemplateResponse,
    AdminTemplateItem,
    UpdatePromptResponse,
    SystemPromptRegenerateResponse
} from '../types/template'

export const templateApi = {
    /**
     * 내 템플릿 목록 조회
     *
     * @returns 템플릿 목록
     */
    listTemplates: async (): Promise<TemplateListItem[]> => {
        const response = await api.get<ApiResponse<TemplateListItem[]>>(API_ENDPOINTS.LIST_TEMPLATES)

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || '템플릿 목록 조회에 실패했습니다.')
        }

        return response.data.data
    },

    /**
     * 관리자: 전체 템플릿 조회
     *
     * @returns 전체 템플릿 목록
     */
    listAllTemplates: async (): Promise<AdminTemplateItem[]> => {
        const response = await api.get<ApiResponse<AdminTemplateItem[]>>(API_ENDPOINTS.ADMIN_LIST_TEMPLATES)

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || '템플릿 목록 조회에 실패했습니다.')
        }

        return response.data.data
    },

    /**
     * 템플릿 상세 조회
     *
     * @param templateId - 템플릿 ID
     * @returns 템플릿 상세 정보
     */
    getTemplate: async (templateId: number): Promise<TemplateDetail> => {
        const response = await api.get<ApiResponse<TemplateDetail>>(API_ENDPOINTS.GET_TEMPLATE(templateId))

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || '템플릿 조회에 실패했습니다.')
        }

        return response.data.data
    },

    /**
     * 템플릿 업로드
     *
     * @param file - HWPX 파일
     * @param title - 템플릿 제목
     * @returns 업로드된 템플릿 정보
     */
    uploadTemplate: async (file: File, title: string): Promise<UploadTemplateResponse> => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('title', title)

        // Content-Type을 제거하여 axios가 자동으로 multipart/form-data boundary를 설정하도록 함
        const response = await api.post<ApiResponse<UploadTemplateResponse>>(API_ENDPOINTS.UPLOAD_TEMPLATE, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || '템플릿 업로드에 실패했습니다.')
        }

        return response.data.data
    },

    /**
     * 템플릿 삭제
     *
     * @param templateId - 삭제할 템플릿 ID
     */
    deleteTemplate: async (templateId: number): Promise<DeleteTemplateResponse> => {
        const response = await api.delete<ApiResponse<DeleteTemplateResponse>>(API_ENDPOINTS.DELETE_TEMPLATE(templateId))

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || '템플릿 삭제에 실패했습니다.')
        }

        return response.data.data
    },

    /**
     * User Prompt 업데이트
     *
     * @param templateId - 템플릿 ID
     * @param promptUser - 새로운 User Prompt
     * @returns 업데이트 응답
     */
    updatePromptUser: async (templateId: number, promptUser: string): Promise<UpdatePromptResponse> => {
        const response = await api.put<ApiResponse<UpdatePromptResponse>>(API_ENDPOINTS.UPDATE_PROMPT_USER(templateId), {
            prompt_user: promptUser
        })

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || 'User Prompt 업데이트에 실패했습니다.')
        }

        return response.data.data
    },

    /**
     * System Prompt 업데이트
     *
     * @param templateId - 템플릿 ID
     * @param promptSystem - 새로운 System Prompt
     * @returns 업데이트 응답
     */
    updatePromptSystem: async (templateId: number, promptSystem: string): Promise<UpdatePromptResponse> => {
        const response = await api.put<ApiResponse<UpdatePromptResponse>>(API_ENDPOINTS.UPDATE_PROMPT_SYSTEM(templateId), {
            prompt_system: promptSystem
        })

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || 'System Prompt 업데이트에 실패했습니다.')
        }

        return response.data.data
    },

    /**
     * System Prompt 재생성
     *
     * @param templateId - 템플릿 ID
     * @returns 재생성 응답
     */
    regeneratePromptSystem: async (templateId: number): Promise<SystemPromptRegenerateResponse> => {
        const response = await api.post<ApiResponse<SystemPromptRegenerateResponse>>(API_ENDPOINTS.REGENERATE_PROMPT_SYSTEM(templateId))

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || 'System Prompt 재생성에 실패했습니다.')
        }

        return response.data.data
    }
}
