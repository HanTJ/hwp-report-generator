/*
 * 사용자 정보 업데이트
 */

export interface UserUpdate {
    is_active?: boolean
    is_admin?: boolean
    password_reset_required?: boolean
}

/*
 * 사용자 목록 응답
 */
export interface UserListResponse {
    users: UserData[]
}

/*
 * 사용자 목록에 노출될 사용자 정보
 */
export interface UserData {
    id: number
    email: string
    username: string
    is_active: boolean
    is_admin: boolean
    password_reset_required: boolean
    created_at: string
}
