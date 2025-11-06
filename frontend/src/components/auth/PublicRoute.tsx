import React from 'react'
import {Navigate} from 'react-router-dom'
import {useAuth} from '../../hooks/useAuth'
import {Spin} from 'antd'

/**
 * PublicRoute.tsx
 *
 * ⭐ 로그인하지 않은 사용자만 접근 가능한 페이지를 보호하는 컴포넌트
 *
 * 라우트 보호(Route Guard)란?
 * - 특정 조건을 만족하지 않으면 페이지 접근을 막음
 * - 이미 로그인한 사용자가 로그인/회원가입 페이지 접근 → 메인 페이지로 리다이렉트
 * - PrivateRoute와 반대 개념 (Public = 비로그인 사용자 전용)
 *
 * 체크하는 조건:
 * 1. 로그인 여부 (isAuthenticated)
 *
 * 사용 방법:
 * <PublicRoute>
 *   <LoginPage />
 * </PublicRoute>
 *
 * <PublicRoute>
 *   <RegisterPage />
 * </PublicRoute>
 *
 * 동작 순서:
 * 1. 로딩 중이면 → 스피너 표시
 * 2. 이미 로그인 했으면 → '/'로 리다이렉트
 * 3. 로그인 안 했으면 → '/login' 또는 '/register' 접근
 */

interface PublicRouteProps {
    children: React.ReactNode // 보호할 페이지 컴포넌트 (로그인, 회원가입 등)
}

const PublicRoute: React.FC<PublicRouteProps> = ({children}) => {
    const {isAuthenticated, isLoading} = useAuth()

    /**
     * 1단계: 로딩 중
     * - 초기 로딩 중에는 스피너 표시
     * - AuthContext에서 로컬스토리지 체크하는 동안 대기
     */
    if (isLoading) {
        return (
            <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh'}}>
                <Spin size="large" />
            </div>
        )
    }

    /**
     * 2단계: 로그인 체크
     * - 이미 로그인 했으면 메인 페이지로 이동
     * - replace: 브라우저 뒤로가기 했을 때 이 페이지로 안 돌아오도록
     *
     * 예시:
     * - 로그인한 상태에서 /login 접속 → /로 리다이렉트
     * - 로그인한 상태에서 /register 접속 → /로 리다이렉트
     */
    if (isAuthenticated) {
        return <Navigate to="/" replace />
    }

    /**
     * 모든 조건 통과 (로그인 안 한 상태)
     * - children(공개 페이지)를 표시
     */
    return <>{children}</>
}

export default PublicRoute
