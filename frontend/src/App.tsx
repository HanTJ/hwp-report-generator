/**
 * App.tsx
 *
 * ⭐ 앱의 최상위 컴포넌트
 *
 * 역할:
 * 1. 전역 설정 (React Query, Ant Design, 인증 Context)
 * 2. 라우팅 설정 (URL별 페이지 매핑)
 *
 * 구조:
 * QueryClient: 서버 데이터 캐싱/관리
 *   → ConfigProvider: Ant Design 한글 설정
 *     → AntdApp: Modal, message 같은 전역 컴포넌트 지원
 *       → AuthProvider: 로그인 사용자 정보 전역 관리
 *         → Router: URL 라우팅
 */

import React from 'react'
import {BrowserRouter as Router, Routes, Route, Navigate} from 'react-router-dom'
import {QueryClient, QueryClientProvider} from '@tanstack/react-query'
import '@ant-design/v5-patch-for-react-19'
import {ConfigProvider, App as AntdApp} from 'antd'
import koKR from 'antd/locale/ko_KR'
import {AuthProvider} from './context/AuthContext'
import PrivateRoute from './components/auth/PrivateRoute'
import PublicRoute from './components/auth/PublicRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import MainPage from './pages/MainPage'
import MainBakPage from './pages/MainBakPage'
import TopicListPage from './pages/TopicListPage'
import ChangePasswordPage from './pages/ChangePasswordPage'
import AdminPage from './pages/AdminPage'

// React Query 설정
// - retry: API 실패 시 1번만 재시도
// - refetchOnWindowFocus: 브라우저 탭 전환 시 자동 새로고침 안 함
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            refetchOnWindowFocus: false
        }
    }
})

const App: React.FC = () => {
    return (
        // React Query: 서버 데이터 캐싱 및 상태 관리
        <QueryClientProvider client={queryClient}>
            {/* Ant Design 한글 설정 */}
            <ConfigProvider locale={koKR}>
                {/* Ant Design App: Modal, message 같은 전역 컴포넌트 사용 가능하게 함 */}
                <AntdApp>
                    {/* 인증 Context: 로그인 사용자 정보를 앱 전체에서 사용 가능 */}
                    <AuthProvider>
                        {/* 라우터: URL에 따라 다른 페이지를 보여줌 */}
                        <Router>
                            <Routes>
                                {/* 공개 라우트: 로그인 안 한 사람만 접근 가능 */}
                                <Route
                                    path="/login"
                                    element={
                                        <PublicRoute>
                                            <LoginPage />
                                        </PublicRoute>
                                    }
                                />
                                <Route
                                    path="/register"
                                    element={
                                        <PublicRoute>
                                            <RegisterPage />
                                        </PublicRoute>
                                    }
                                />

                                {/* 보호된 라우트: 로그인한 사람만 접근 가능 */}
                                <Route
                                    path="/"
                                    element={
                                        <PrivateRoute>
                                            <MainPage />
                                        </PrivateRoute>
                                    }
                                />
                                <Route
                                    path="/bak"
                                    element={
                                        <PrivateRoute>
                                            <MainBakPage />
                                        </PrivateRoute>
                                    }
                                />
                                <Route
                                    path="/change-password"
                                    element={
                                        <PrivateRoute>
                                            <ChangePasswordPage />
                                        </PrivateRoute>
                                    }
                                />
                                <Route
                                    path="/topics"
                                    element={
                                        <PrivateRoute>
                                            <TopicListPage />
                                        </PrivateRoute>
                                    }
                                />

                                {/* 관리자 전용 라우트: 관리자만 접근 가능 */}
                                <Route
                                    path="/admin"
                                    element={
                                        <PrivateRoute requireAdmin={true}>
                                            <AdminPage />
                                        </PrivateRoute>
                                    }
                                />

                                {/* 존재하지 않는 URL은 홈으로 리다이렉트 */}
                                <Route path="*" element={<Navigate to="/" replace />} />
                            </Routes>
                        </Router>
                    </AuthProvider>
                </AntdApp>
            </ConfigProvider>
        </QueryClientProvider>
    )
}

export default App
