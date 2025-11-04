export interface UserUpdate {
    is_active?: boolean
    is_admin?: boolean
    password_reset_required?: boolean
}

export interface UserListResponse {
    users: UserData[]
}

export interface UserData {
    id: number
    email: string
    username: string
    is_active: boolean
    is_admin: boolean
    password_reset_required: boolean
    created_at: string
}
