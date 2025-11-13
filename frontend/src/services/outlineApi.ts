import api from './api'

/**
 * Outline API Service
 *
 * ⚠️ 중요: 이 API는 MSW(Mock Service Worker)로 mock 처리됩니다.
 *
 * Mock 설정 위치:
 * - frontend/src/mocks/handlers.ts
 *
 * Mock 여부 확인 방법:
 * 1. 브라우저 콘솔에서: window.listMockAPIs()
 * 2. Network 탭에서: (from service worker) 표시 확인
 * 3. 코드에서: import { isMockedEndpoint } from '../mocks/handlers'
 *
 * Backend API 없이 Frontend만 개발할 때 사용합니다.
 * 실제 Backend 구현 시 MSW 핸들러를 제거하면 자동으로 실제 API 호출됩니다.
 */

export interface OutlineRequest {
    id: number  // 0, 1, 2, 3... 순차적 번호
    message: string
}

export interface OutlineResponse {
    id: number  // Backend에서 반환하는 숫자 ID
    outline: string
    timestamp: number
}

/**
 * 개요 API 서비스
 * MSW가 활성화되면 /api/outlines/ask는 mock 응답 반환
 */
export const outlineApi = {
    /**
     * 개요 요청
     * @param request 사용자 메시지 + 이전 개요 이력
     * @returns 개요 응답
     */
    askOutline: async (request: OutlineRequest): Promise<OutlineResponse> => {
        console.log('outlineApi.askOutline > request >', request)
        const response = await api.post<OutlineResponse>('/api/outlines/ask', request)
        console.log('outlineApi.askOutline > response >', response.data)
        return response.data
    }
}
