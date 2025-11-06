import {useState, useEffect, useCallback} from 'react'
import {adminApi} from '../services/adminApi'
import type {UserData} from '../types/user'

/**
 * useUsers.ts
 *
 * ⭐ 사용자 관리 로직을 담은 Custom Hook (Axios 기반)
 *
 * 역할:
 * 1. useState: 사용자 목록 및 로딩 상태 관리
 * 2. useEffect: 컴포넌트 마운트 시 사용자 목록 자동 로드
 * 3. Axios: 서버 API 호출 (사용자 조회/승인/거부/비밀번호 초기화)
 *
 * 사용 방법:
 * const { users, isLoading, refetch, approveUser, rejectUser, resetPassword } = useUsers();
 */

export const useUsers = () => {
    // 상태 관리
    const [users, setUsers] = useState<UserData[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    /**
     * 사용자 목록 로드
     * - API 호출하여 사용자 목록 가져오기
     * - 로딩 상태 관리
     */
    const loadUsers = useCallback(async () => {
        setIsLoading(true)
        setError(null)

        try {
            const usersList = await adminApi.listUsers()
            setUsers(usersList)
        } catch (err) {
            console.error('Failed to load users:', err)
            setError(err as Error)
            setUsers([])
        } finally {
            setIsLoading(false)
        }
    }, [])

    /**
     * 컴포넌트 마운트 시 자동으로 사용자 목록 로드
     */
    useEffect(() => {
        loadUsers()
    }, [loadUsers])

    /**
     * 수동 새로고침 함수
     * - 새로고침 버튼 클릭 시 사용
     */
    const refetch = useCallback(async () => {
        await loadUsers()
    }, [loadUsers])

    /**
     * 사용자 승인 (is_active를 true로 변경)
     * @param userId - 승인할 사용자 ID
     * @returns 성공 메시지
     */
    const approveUser = useCallback(
        async (userId: number) => {
            try {
                const result = await adminApi.approveUser(userId)

                // 로컬 상태 업데이트 (즉시 반영)
                setUsers((prevUsers) =>
                    prevUsers.map((user) => (user.id === userId ? {...user, is_active: true} : user))
                )

                return result
            } catch (err) {
                console.error('Failed to approve user:', err)
                throw err
            }
        },
        []
    )

    /**
     * 사용자 거부 (is_active를 false로 변경)
     * @param userId - 거부할 사용자 ID
     * @returns 성공 메시지
     */
    const rejectUser = useCallback(
        async (userId: number) => {
            try {
                const result = await adminApi.rejectUser(userId)

                // 로컬 상태 업데이트 (즉시 반영)
                setUsers((prevUsers) =>
                    prevUsers.map((user) => (user.id === userId ? {...user, is_active: false} : user))
                )

                return result
            } catch (err) {
                console.error('Failed to reject user:', err)
                throw err
            }
        },
        []
    )

    /**
     * 비밀번호 초기화
     * @param userId - 비밀번호 초기화할 사용자 ID
     * @returns 임시 비밀번호 정보
     */
    const resetPassword = useCallback(
        async (userId: number) => {
            try {
                const result = await adminApi.resetPassword(userId)

                // 로컬 상태 업데이트 (password_reset_required를 true로)
                setUsers((prevUsers) =>
                    prevUsers.map((user) => (user.id === userId ? {...user, password_reset_required: true} : user))
                )

                return result
            } catch (err) {
                console.error('Failed to reset password:', err)
                throw err
            }
        },
        []
    )

    /**
     * Hook에서 반환하는 값들
     * - users: 사용자 목록 배열
     * - isLoading: 로딩 중인지
     * - error: 에러 객체 (에러 없으면 null)
     * - refetch: 수동 새로고침 함수
     * - approveUser, rejectUser, resetPassword: 변경 작업 함수들
     */
    return {
        users,
        isLoading,
        error,
        refetch,
        approveUser,
        rejectUser,
        resetPassword
    }
}
