/**
 * PrivateRoute.tsx
 *
 * ⭐ 로그인한 사용자만 접근 가능한 페이지를 보호하는 컴포넌트
 *
 * 라우트 보호(Route Guard)란?
 * - 특정 조건을 만족하지 않으면 페이지 접근을 막음
 * - 로그인 안 한 사용자가 메인 페이지 접근 → 로그인 페이지로 리다이렉트
 * - 일반 사용자가 관리자 페이지 접근 → 메인 페이지로 리다이렉트
 *
 * 체크하는 조건:
 * 1. 로그인 여부 (isAuthenticated)
 * 2. 비밀번호 변경 필요 여부 (password_reset_required)
 * 3. 관리자 권한 (requireAdmin)
 *
 * 사용 방법:
 * <PrivateRoute>
 *   <MainPage />
 * </PrivateRoute>
 *
 * <PrivateRoute requireAdmin={true}>
 *   <AdminPage />
 * </PrivateRoute>
 */

import React from 'react'
import {Navigate, useLocation} from 'react-router-dom'
import {useAuth} from '../../hooks/useAuth'
import {Spin} from 'antd'

interface PrivateRouteProps {
    children: React.ReactNode // 보호할 페이지 컴포넌트
    requireAdmin?: boolean // 관리자만 접근 가능한지 (기본값: false)
}

/**
 * PrivateRoute 컴포넌트
 *
 * 동작 순서:
 * 1. 로딩 중이면 → 스피너 표시
 * 2. 로그인 안 했으면 → /login으로 리다이렉트
 * 3. 비밀번호 변경 필요하면 → /change-password로 리다이렉트
 * 4. 관리자 권한 필요한데 없으면 → /로 리다이렉트
 * 5. 모든 조건 통과 → 페이지 표시
 */
const PrivateRoute: React.FC<PrivateRouteProps> = ({children, requireAdmin = false}) => {
    const {user, isAuthenticated, isLoading} = useAuth()
    const location = useLocation() // 현재 URL 정보

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
     * - 로그인 안 했으면 로그인 페이지로 이동
     * - state={{ from: location }}: 로그인 후 원래 가려던 페이지로 돌아가기 위해 현재 위치 저장
     * - replace: 브라우저 뒤로가기 했을 때 이 페이지로 안 돌아오도록
     */
    if (!isAuthenticated) {
        return <Navigate to="/login" state={{from: location}} replace />
    }

    /**
     * 3단계: 비밀번호 변경 필요 여부 체크
     * - 관리자가 비밀번호 초기화 했으면 password_reset_required가 true
     * - 비밀번호 변경 페이지 외의 모든 페이지 접근 시 비밀번호 변경 페이지로 강제 이동
     */
    if (user?.password_reset_required && location.pathname !== '/change-password') {
        return <Navigate to="/change-password" replace />
    }

    /**
     * 4단계: 관리자 권한 체크
     * - requireAdmin이 true인데 is_admin이 false면
     * - 메인 페이지로 리다이렉트
     */
    if (requireAdmin && !user?.is_admin) {
        return <Navigate to="/" replace />
    }

    /**
     * 모든 조건 통과
     * - children(보호된 페이지)를 표시
     */
    return <>{children}</>
}

export default PrivateRoute
