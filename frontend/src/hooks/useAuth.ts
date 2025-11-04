import {useContext} from 'react'
import {AuthContext} from '../context/AuthContext'

/**
 * useAuth.ts
 *
 * ⭐ AuthContext를 편리하게 사용하기 위한 Custom Hook
 *
 * Hook이란?
 * - 리액트의 기능(state, context 등)을 "끌어다 쓰는" 함수
 * - use로 시작하는 함수
 *
 * 이 Hook의 역할:
 * 1. AuthContext의 값을 가져옴
 * 2. AuthProvider 없이 사용하면 에러 발생 (안전장치)
 *
 * 사용 방법:
 * const { user, login, logout, isAuthenticated } = useAuth();
 *
 * 사용 예시:
 * function LoginPage() {
 *   const { login } = useAuth();
 *   const handleLogin = async () => {
 *     await login({ email, password });
 *   };
 * }
 */

/**
 * useAuth Custom Hook
 *
 * @returns AuthContext의 값 (user, login, logout 등)
 * @throws AuthProvider로 감싸지 않은 경우 에러 발생
 */
export const useAuth = () => {
    // useContext로 AuthContext의 값을 가져옴
    const context = useContext(AuthContext)

    // context가 undefined라면 AuthProvider 밖에서 사용한 것 → 에러
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }

    // Context 값 반환
    return context
}
