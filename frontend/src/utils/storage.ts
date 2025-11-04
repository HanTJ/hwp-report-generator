/**
 * storage.ts
 *
 * ⭐ 로컬스토리지(브라우저 저장소)를 관리하는 유틸리티
 *
 * 로컬스토리지란?
 * - 브라우저에 데이터를 저장하는 공간
 * - 페이지를 새로고침하거나 닫아도 데이터가 유지됨
 * - 로그인 토큰, 사용자 정보 등을 저장
 *
 * 이 파일이 관리하는 데이터:
 * 1. access_token: 로그인 인증 토큰
 * 2. user: 로그인한 사용자 정보
 *
 * 사용 방법:
 * import { storage } from './utils/storage';
 * storage.setToken('토큰값');
 * const token = storage.getToken();
 */

import {STORAGE_KEYS} from '../constants/'
import type {User} from '../types/auth'

export const storage = {
    /**
     * 토큰 가져오기
     * @returns 저장된 토큰 또는 null
     */
    getToken: (): string | null => {
        return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
    },

    /**
     * 토큰 저장하기
     * @param token 저장할 토큰
     */
    setToken: (token: string): void => {
        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token)
    },

    /**
     * 토큰 삭제하기
     */
    removeToken: (): void => {
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    },

    /**
     * 사용자 정보 가져오기
     * - 로컬스토리지에 JSON 문자열로 저장된 사용자 정보를 객체로 변환
     * @returns 사용자 객체 또는 null
     */
    getUser: (): User | null => {
        const userStr = localStorage.getItem(STORAGE_KEYS.USER)
        if (!userStr) return null

        try {
            // JSON 문자열 → 객체로 변환
            return JSON.parse(userStr)
        } catch {
            // 파싱 실패 시 null 반환
            return null
        }
    },

    /**
     * 사용자 정보 저장하기
     * - 객체를 JSON 문자열로 변환하여 저장
     * @param user 저장할 사용자 객체
     */
    setUser: (user: User): void => {
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user))
    },

    /**
     * 사용자 정보 삭제하기
     */
    removeUser: (): void => {
        localStorage.removeItem(STORAGE_KEYS.USER)
    },

    /**
     * 모든 인증 데이터 삭제 (로그아웃 시 사용)
     * - 토큰과 사용자 정보 모두 삭제
     */
    clear: (): void => {
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
        localStorage.removeItem(STORAGE_KEYS.USER)
    }
}
