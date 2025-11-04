import api from './api'
import {API_ENDPOINTS} from '../constants/'
import type {UserData} from '../types/user'
import type {ApiResponse} from '../types/api'

interface MessageResponse {
    message: string
}

interface PasswordResetResponse {
    message: string
    temporary_password: string
}

interface UsersListResponse {
    users: UserData[]
    total: number
}

export const adminApi = {
    listUsers: async (): Promise<UserData[]> => {
        const response = await api.get<ApiResponse<UsersListResponse>>(API_ENDPOINTS.LIST_USERS)

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || '사용자 목록 조회에 실패했습니다.')
        }

        return response.data.data.users
    },

    approveUser: async (userId: number): Promise<MessageResponse> => {
        const response = await api.patch<ApiResponse<MessageResponse>>(API_ENDPOINTS.APPROVE_USER(userId))

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || '사용자 승인에 실패했습니다.')
        }

        return response.data.data
    },

    rejectUser: async (userId: number): Promise<MessageResponse> => {
        const response = await api.patch<ApiResponse<MessageResponse>>(API_ENDPOINTS.REJECT_USER(userId))

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || '사용자 거부에 실패했습니다.')
        }

        return response.data.data
    },

    resetPassword: async (userId: number): Promise<PasswordResetResponse> => {
        const response = await api.post<ApiResponse<PasswordResetResponse>>(API_ENDPOINTS.RESET_PASSWORD(userId))

        if (!response.data.success || !response.data.data) {
            throw new Error(response.data.error?.message || '비밀번호 초기화에 실패했습니다.')
        }

        return response.data.data
    }
}
