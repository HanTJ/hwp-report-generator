/**
 * AuthContext.tsx
 *
 * ⭐ 인증(로그인) 정보를 앱 전체에서 공유하는 Context
 *
 * Context란?
 * - 여러 컴포넌트가 공유하는 "전역 상태 저장소"
 * - props를 계속 전달하지 않고도 어디서든 데이터를 꺼내 쓸 수 있음
 *
 * 이 Context가 관리하는 것:
 * 1. user: 현재 로그인한 사용자 정보
 * 2. isAuthenticated: 로그인 여부 (true/false)
 * 3. isLoading: 초기 로딩 상태
 * 4. login, register, logout, changePassword: 인증 관련 함수들
 *
 * 사용 방법:
 * const { user, login, logout } = useAuth();
 */

import React, { createContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User, LoginRequest, RegisterRequest, ChangePasswordRequest } from '../types/auth';
import { authApi } from '../services/authApi';
import { storage } from '../utils/storage';

/**
 * AuthContext의 타입 정의
 * - Context에서 제공할 값들의 타입을 정의
 */
interface AuthContextType {
  user: User | null;                                     // 현재 로그인한 사용자 (로그인 안 했으면 null)
  isAuthenticated: boolean;                              // 로그인 여부
  isLoading: boolean;                                    // 초기 로딩 중인지
  login: (data: LoginRequest) => Promise<void>;          // 로그인 함수
  register: (data: RegisterRequest) => Promise<void>;    // 회원가입 함수
  logout: () => void;                                    // 로그아웃 함수
  changePassword: (data: ChangePasswordRequest) => Promise<void>;  // 비밀번호 변경 함수
}

/**
 * Context 생성
 * - 초기값은 undefined (AuthProvider로 감싸지 않으면 에러 발생하도록)
 */
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider의 Props 타입
 * - children: 이 Provider로 감쌀 하위 컴포넌트들
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider 컴포넌트
 *
 * 역할:
 * 1. 로그인 상태를 관리 (user, isAuthenticated, isLoading)
 * 2. 인증 관련 함수들을 제공 (login, logout 등)
 * 3. 페이지 새로고침 시 로컬스토리지에서 사용자 정보 복구
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // 상태 관리
  const [user, setUser] = useState<User | null>(null);  // 현재 로그인한 사용자
  const [isLoading, setIsLoading] = useState(true);     // 초기 로딩 상태

  /**
   * 컴포넌트가 처음 렌더링될 때 실행
   * - 로컬스토리지에 저장된 토큰과 사용자 정보가 있으면 복구
   * - 페이지 새로고침해도 로그인 상태 유지
   */
  useEffect(() => {
    const token = storage.getToken();
    const savedUser = storage.getUser();

    if (token && savedUser) {
      setUser(savedUser);  // 로그인 상태 복구
    }
    setIsLoading(false);  // 로딩 완료
  }, []);  // [] = 컴포넌트 마운트 시 1번만 실행

  /**
   * 로그인 함수
   *
   * 1. authApi.login()으로 서버에 로그인 요청
   * 2. 성공하면 토큰과 사용자 정보를 로컬스토리지에 저장
   * 3. user 상태 업데이트 → 앱 전체에 로그인 상태 반영
   */
  const login = async (data: LoginRequest) => {
    const response = await authApi.login(data);
    storage.setToken(response.access_token);  // 토큰 저장
    storage.setUser(response.user);           // 사용자 정보 저장
    setUser(response.user);                   // 상태 업데이트
  };

  /**
   * 회원가입 함수
   * - 서버에 회원가입 요청만 보냄
   * - 자동 로그인하지 않음 (관리자 승인 필요)
   */
  const register = async (data: RegisterRequest) => {
    await authApi.register(data);
  };

  /**
   * 로그아웃 함수
   * 1. 로컬스토리지 전체 삭제
   * 2. user 상태를 null로 설정
   */
  const logout = () => {
    storage.clear();
    setUser(null);
  };

  /**
   * 비밀번호 변경 함수
   * 1. 서버에 비밀번호 변경 요청
   * 2. 성공하면 password_reset_required 플래그를 false로 변경
   * 3. 로컬스토리지와 상태 업데이트
   */
  const changePassword = async (data: ChangePasswordRequest) => {
    await authApi.changePassword(data);
    if (user) {
      const updatedUser = { ...user, password_reset_required: false };
      storage.setUser(updatedUser);
      setUser(updatedUser);
    }
  };

  /**
   * Context에서 제공할 값들
   * - 이 값들을 하위 컴포넌트에서 useAuth()로 사용 가능
   */
  const value = {
    user,
    isAuthenticated: !!user,  // user가 있으면 true, 없으면 false
    isLoading,
    login,
    register,
    logout,
    changePassword,
  };

  // Provider로 하위 컴포넌트들을 감싸고, value를 제공
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
