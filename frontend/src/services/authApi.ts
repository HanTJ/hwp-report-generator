/**
 * authApi.ts
 *
 * 인증 관련 API 함수 모음
 * - 로그인, 회원가입, 비밀번호 변경
 */

import api from "./api";
import { API_ENDPOINTS } from "../constants/";
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  ChangePasswordRequest,
} from "../types/auth";

export const authApi = {
  /**
   * 로그인
   * POST /api/auth/login
   * @param data 이메일, 비밀번호
   * @returns 토큰, 사용자 정보
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    console.log("authApi.login called with data:", data);
    const response = await api.post<LoginResponse>(API_ENDPOINTS.LOGIN, data);
    return response.data;
  },

  /**
   * 회원가입
   * POST /api/auth/register
   * @param data 이메일, 사용자명, 비밀번호
   */
  register: async (data: RegisterRequest): Promise<void> => {
    await api.post(API_ENDPOINTS.REGISTER, data);
  },

  /**
   * 비밀번호 변경
   * POST /api/auth/change-password
   * @param data 현재 비밀번호, 새 비밀번호
   */
  changePassword: async (data: ChangePasswordRequest): Promise<void> => {
    await api.post(API_ENDPOINTS.CHANGE_PASSWORD, data);
  },
};
