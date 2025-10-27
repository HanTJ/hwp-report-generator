import api from './api';
import { API_ENDPOINTS } from '../constants/';
import type { UserData } from '../types/user';

interface MessageResponse {
  message: string;
}

interface PasswordResetResponse {
  message: string;
  temporary_password: string;
}

export const adminApi = {
  listUsers: async (): Promise<UserData[]> => {
    const response = await api.get<UserData[]>(API_ENDPOINTS.LIST_USERS);
    return response.data;
  },

  approveUser: async (userId: number): Promise<MessageResponse> => {
    const response = await api.patch<MessageResponse>(API_ENDPOINTS.APPROVE_USER(userId));
    return response.data;
  },

  rejectUser: async (userId: number): Promise<MessageResponse> => {
    const response = await api.patch<MessageResponse>(API_ENDPOINTS.REJECT_USER(userId));
    return response.data;
  },

  resetPassword: async (userId: number): Promise<PasswordResetResponse> => {
    const response = await api.post<PasswordResetResponse>(API_ENDPOINTS.RESET_PASSWORD(userId));
    return response.data;
  },
};
