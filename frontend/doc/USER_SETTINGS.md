# User Settings (사용자 설정)

사용자 설정 관리 및 정보 조회 기능

## 📋 목차

1. [개요](#개요)
2. [컴포넌트 구조](#컴포넌트-구조)
3. [기능 명세](#기능-명세)
4. [UI 구조](#ui-구조)
5. [API 연동](#api-연동)
6. [파일 구조](#파일-구조)
7. [구현 히스토리](#구현-히스토리)

---

## 개요

### 목적

1. 일반 설정 관리 (다크모드 등)
2. 사용자 정보 조회 (이메일, 사용자명, 가입일)

### 접근 경로

MainPage의 Sidebar 하단 → **사용자 버튼 클릭** → **드롭다운 메뉴** → **"설정"** 선택

---

## 컴포넌트 구조

### SettingsModal

**파일**: `frontend/src/components/user/SettingsModal.tsx`

#### Props

```typescript
interface SettingsModalProps {
    /** null이면 내 정보 조회 (API), UserData 전달 시 해당 데이터 표시 */
    user: UserData | null
    isOpen: boolean
    onClose: () => void
}
```

#### State

```typescript
type TabType = 'general' | 'profile'

// 상태 변수들
const [userData, setUserData] = useState<UserData | null>(user)
const [loading, setLoading] = useState(false)
const [activeTab, setActiveTab] = useState<TabType>('profile')
const [isDarkMode, setIsDarkMode] = useState(false) // UI만, 기능 미구현
```

#### 주요 함수

**loadMyInfo()**

```typescript
const loadMyInfo = async () => {
    setLoading(true)
    try {
        const data = await authApi.getMyInfo()
        setUserData(data)
    } catch (error: any) {
        message.error('사용자 정보를 불러올 수 없습니다.')
    } finally {
        setLoading(false)
    }
}
```

**formatDate()**

```typescript
const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}
```

---

## 기능 명세

### 탭 구조

#### 1️⃣ 일반 (General) 탭

- **탭 라벨**: "일반"
- **아이콘**: ⚙️ `<SettingOutlined />`
- **Content Header**: "일반"

**기능**

**다크 모드 설정**

- 라벨: "다크 모드"
- 컴포넌트: `<Switch>`
- 상태: `isDarkMode`
- **주의**: UI만 구현됨, 실제 다크모드 기능은 미구현

#### 2️⃣ 사용자 정보 (Profile) 탭

- **탭 라벨**: "사용자 정보"
- **아이콘**: 👤 `<UserOutlined />`
- **Content Header**: "사용자 정보"

**표시 정보**:

- 이메일: `userData.email`
- 사용자명: `userData.username`
- 가입일: `userData.created_at` (`formatDate()` 적용)

**로딩 상태**:

- `<Spin size="large" />` 표시
- 메시지: "사용자 정보를 불러오는 중..."

**에러 상태**:

- 메시지: "사용자 정보를 불러올 수 없습니다."

---

## UI 구조

### 컴포넌트 계층 구조

```tsx
<Modal>
    <modalContainer>
        <modalBody>
            {/* Left Sidebar */}
            <sidebar>
                <sidebarHeader>
                    <CloseOutlined /> {/* X 버튼 */}
                </sidebarHeader>
                <sidebarMenu>
                    <tabButton active={activeTab === 'general'}>
                        <SettingOutlined /> 일반
                    </tabButton>
                    <tabButton active={activeTab === 'profile'}>
                        <UserOutlined /> 사용자 정보
                    </tabButton>
                </sidebarMenu>
            </sidebar>

            {/* Right Content */}
            <content>
                <contentHeader>
                    <h2>{activeTab === 'general' ? '일반' : '사용자 정보'}</h2>
                </contentHeader>
                <tabContent>{/* 일반 탭 또는 사용자 정보 탭 내용 */}</tabContent>
            </content>
        </modalBody>
    </modalContainer>
</Modal>
```

### 헤더 높이 통일

- **Desktop**: sidebarHeader, contentHeader 모두 60px
- **Mobile (≤768px)**: sidebarHeader, contentHeader 모두 50px

---

## API 연동

### GET /api/auth/me

**목적**: 현재 로그인한 사용자 정보 조회

**호출**:

```typescript
// frontend/src/services/authApi.ts
getMyInfo: async (): Promise<UserData> => {
    const response = await api.get<ApiResponse<UserData>>(API_ENDPOINTS.ME)

    if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error?.message || '사용자 정보를 불러올 수 없습니다.')
    }

    return response.data.data
}
```

**응답 타입** (`UserData`):

```typescript
interface UserData {
    id: number
    email: string
    username: string
    is_active: boolean // 모달에 표시하지 않음
    is_admin: boolean // 모달에 표시하지 않음
    password_reset_required: boolean // 모달에 표시하지 않음
    created_at: string // ISO 8601 형식
}
```

**API 응답 예시**:

```json
{
    "success": true,
    "data": {
        "id": 1,
        "email": "user@example.com",
        "username": "홍길동",
        "is_active": true,
        "is_admin": false,
        "password_reset_required": false,
        "created_at": "2025-01-01T09:00:00Z"
    },
    "error": null,
    "meta": {
        "requestId": "req_abc123"
    },
    "feedback": []
}
```

**에러 처리**:

```typescript
try {
    const data = await authApi.getMyInfo()
    setUserData(data)
} catch (error: any) {
    message.error('사용자 정보를 불러올 수 없습니다.')
}
```

---

## 파일 구조

### 컴포넌트 파일

```
frontend/src/components/user/
├── SettingsModal.tsx           # 메인 컴포넌트
└── SettingsModal.module.css    # 스타일시트
```

### 관련 파일

```
frontend/src/
├── services/
│   └── authApi.ts              # getMyInfo() 메서드
├── components/layout/
│   └── Sidebar.tsx             # 드롭다운 메뉴 통합
└── types/
    └── user.ts                 # UserData 타입 정의
```

---

## 구현 히스토리

### 2025-01-05 - 전체 구현

#### Phase 1: 백엔드 확인 및 API 클라이언트

1. ✅ `GET /api/auth/me` 엔드포인트 확인
2. ✅ `authApi.getMyInfo()` 메서드 구현

#### Phase 2: 컴포넌트 초기 구현

1. ✅ SettingsModal 기본 구조 생성
2. ✅ API 연동 및 로딩 처리
3. ✅ 사용자 정보 표시 (이메일, 사용자명, 가입일)

#### Phase 3: 탭 구조 추가

1. ✅ 좌측 사이드바 추가
2. ✅ "일반" / "사용자 정보" 탭 구현
3. ✅ 탭 전환 로직 구현
4. ✅ 다크모드 스위치 UI 추가 (기능 미구현)

#### Phase 5: 호출부 구현

1. ✅ Sidebar 바텀 메뉴를 드롭다운으로 변경
2. ✅ 드롭다운 메뉴에 "설정" 아이템 추가

---

## 사용 예시

### Sidebar에서 모달 열기

```tsx
import React, {useState} from 'react'
import {Dropdown} from 'antd'
import type {MenuProps} from 'antd'
import {SettingOutlined, LogoutOutlined} from '@ant-design/icons'
import SettingsModal from '../user/SettingsModal'

const Sidebar = () => {
    const [isSettingsOpen, setIsSettingsOpen] = useState(false)
    const {user, logout} = useAuth()

    // 드롭다운 메뉴 아이템
    const userMenuItems: MenuProps['items'] = [
        {
            key: 'email',
            label: user?.email,
            disabled: true
        },
        {
            key: 'settings',
            label: '설정',
            icon: <SettingOutlined />,
            onClick: () => setIsSettingsOpen(true)
        },
        {
            type: 'divider'
        },
        {
            key: 'logout',
            label: '로그아웃',
            icon: <LogoutOutlined />,
            onClick: logout
        }
    ]

    return (
        <>
            <Dropdown menu={{items: userMenuItems}} trigger={['click']}>
                <button>
                    <UserOutlined />
                    <span>{user?.username}</span>
                </button>
            </Dropdown>

            {/* Settings Modal */}
            <SettingsModal user={null} isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
        </>
    )
}
```

---

## 향후 개선 사항

### 기능 추가

- [ ] 다크모드 실제 구현
- [ ] 비밀번호 변경 기능

---

## 참고 자료

### 관련 컴포넌트

- [Sidebar](./src/components/layout/Sidebar.tsx)
- [authApi](./src/services/authApi.ts)

---

**작성일**: 2025-01-05
**버전**: 1.0.0
