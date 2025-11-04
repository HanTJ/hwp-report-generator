import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query'
import {adminApi} from '../services/adminApi'
import type {UserData} from '../types/user'

/**
 * useUsers.ts
 *
 * ⭐ 사용자 관리 로직을 담은 Custom Hook
 *
 * React Query란?
 * - 서버 데이터를 캐싱하고 관리하는 라이브러리
 * - 자동으로 로딩, 에러, 데이터 상태를 관리
 * - 데이터를 메모리에 캐시해서 불필요한 API 요청 감소
 * - staleTime: 기본값 0, 즉시 오래된 데이터로 간주 (캐싱값 보여주고 매번 재요청)
 * - gcTime: 기본값 5분, 사용되지 않는 데이터 5분 후 메모리에서 제거
 *
 * 이 Hook의 역할:
 * 1. useQuery: 서버 데이터 조회(사용자 목록 조회) + 캐싱
 * 2. useMutation: 서버 데이터 생성, 수정, 삭제(사용자 승인/거부/비밀번호 초기화)
 * 3. Optimistic Update: 즉각적인 UI 반응 (서버 응답 전에 UI 먼저 업데이트)
 *
 * Optimistic Update란?
 * - "낙관적 업데이트" = 성공할 거라고 믿고 미리 UI 업데이트
 * - 서버 응답 기다리지 않고 즉시 화면 반영 → 빠른 사용자 경험
 * - 실패하면 이전 상태로 롤백
 *
 * 사용 방법:
 * const { users, isLoading, approveUser, rejectUser } = useUsers();
 */

export const useUsers = () => {
    // QueryClient: React Query의 캐시를 관리하는 객체
    const queryClient = useQueryClient()

    /**
     * useQuery: 데이터 조회 (GET 요청)
     *
     * - queryKey: ['users'] - 이 데이터의 고유 식별자 (캐시 키)
     * - queryFn: adminApi.listUsers - 실제 데이터를 가져오는 함수
     *
     * 자동으로 제공되는 것:
     * - data: 서버에서 받은 데이터
     * - isLoading: 로딩 중인지
     * - refetch: 수동으로 다시 불러오기
     */
    const {
        data: usersData,
        isLoading,
        refetch
    } = useQuery({
        queryKey: ['users'],
        queryFn: adminApi.listUsers
    })

    /**
     * useMutation: 데이터 변경 (POST, PUT, PATCH, DELETE)
     *
     * approveMutation: 사용자 승인 (is_active를 true로)
     *
     * Optimistic Update 흐름:
     * 1. onMutate: API 요청 전 실행 → 즉시 UI 업데이트
     * 2. mutationFn: 실제 API 요청
     * 3. onError: 실패 시 → 이전 상태로 롤백
     * 4. onSettled: 성공/실패 관계없이 → 서버 데이터와 동기화
     */
    const approveMutation = useMutation({
        // 실제 API 요청 함수
        mutationFn: (userId: number) => adminApi.approveUser(userId),

        /**
         * onMutate: API 요청 전에 즉시 실행 (Optimistic Update)
         *
         * 1. 진행 중인 쿼리 취소 (충돌 방지)
         * 2. 현재 데이터 백업 (롤백용)
         * 3. 캐시 데이터 즉시 업데이트 (UI 바로 반영)
         * 4. 백업 데이터 반환 (onError에서 사용)
         */
        onMutate: async (userId: number) => {
            // 1. users 쿼리 취소 (충돌 방지)
            await queryClient.cancelQueries({queryKey: ['users']})

            // 2. 현재 데이터 백업
            const previousUsers = queryClient.getQueryData<UserData[]>(['users'])

            // 3. 캐시 즉시 업데이트 (is_active: true로 변경)
            queryClient.setQueryData<UserData[]>(['users'], (old) => {
                if (!old) return old
                return old.map((user) => (user.id === userId ? {...user, is_active: true} : user))
            })

            // 4. 롤백용 데이터 반환
            return {previousUsers}
        },

        /**
         * onError: API 실패 시 실행
         * - 백업해둔 이전 데이터로 롤백
         */
        onError: (_err, _userId, context) => {
            if (context?.previousUsers) {
                queryClient.setQueryData(['users'], context.previousUsers)
            }
        },

        /**
         * onSettled: 성공/실패 관계없이 실행
         * - 서버 데이터를 다시 가져와서 최종 동기화
         */
        onSettled: () => {
            queryClient.invalidateQueries({queryKey: ['users']})
        }
    })

    /**
     * rejectMutation: 사용자 거부 (is_active를 false로)
     * - approveMutation과 동일한 패턴
     * - is_active만 false로 변경
     */
    const rejectMutation = useMutation({
        mutationFn: (userId: number) => adminApi.rejectUser(userId),
        onMutate: async (userId: number) => {
            await queryClient.cancelQueries({queryKey: ['users']})
            const previousUsers = queryClient.getQueryData<UserData[]>(['users'])

            queryClient.setQueryData<UserData[]>(['users'], (old) => {
                if (!old) return old
                return old.map((user) => (user.id === userId ? {...user, is_active: false} : user))
            })

            return {previousUsers}
        },
        onError: (_err, _userId, context) => {
            if (context?.previousUsers) {
                queryClient.setQueryData(['users'], context.previousUsers)
            }
        },
        onSettled: () => {
            queryClient.invalidateQueries({queryKey: ['users']})
        }
    })

    /**
     * resetPasswordMutation: 비밀번호 초기화
     * - password_reset_required를 true로 변경
     */
    const resetPasswordMutation = useMutation({
        mutationFn: (userId: number) => adminApi.resetPassword(userId),
        onMutate: async (userId: number) => {
            await queryClient.cancelQueries({queryKey: ['users']})
            const previousUsers = queryClient.getQueryData<UserData[]>(['users'])

            queryClient.setQueryData<UserData[]>(['users'], (old) => {
                if (!old) return old
                return old.map((user) => (user.id === userId ? {...user, password_reset_required: true} : user))
            })

            return {previousUsers}
        },
        onError: (_err, _userId, context) => {
            if (context?.previousUsers) {
                queryClient.setQueryData(['users'], context.previousUsers)
            }
        },
        onSettled: () => {
            queryClient.invalidateQueries({queryKey: ['users']})
        }
    })

    /**
     * Hook에서 반환하는 값들
     * - users: 사용자 목록 배열
     * - isLoading: 로딩 중인지
     * - refetch: 수동 새로고침 함수
     * - approveUser, rejectUser, resetPassword: 변경 작업 함수들
     */
    return {
        users: usersData || [],
        isLoading,
        refetch,
        approveUser: approveMutation.mutateAsync,
        rejectUser: rejectMutation.mutateAsync,
        resetPassword: resetPasswordMutation.mutateAsync
    }
}
