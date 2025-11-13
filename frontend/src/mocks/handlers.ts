import {http, HttpResponse, delay} from 'msw'

/**
 * MSW Mock API 핸들러
 *
 * 🔵 Mock 처리되는 API (MSW intercept):
 *   - POST /api/outlines/ask - 개요 생성 API
 *   - GET /api/topics/:topicId/messages - 메시지 목록 조회
 *   - POST /api/topics/generate - 보고서 생성 (실제 topicId도 생성)
 *   - GET /api/artifacts/topics/:topicId - 토픽별 아티팩트 목록 조회
 *   - GET /api/artifacts/:artifactId/content - 아티팩트 내용 조회 (MD)
 *
 * ⚪ Passthrough API (실제 Backend 호출):
 *   - POST /api/topics/generate - 보고서 생성
 *   - GET /api/topics - 토픽 목록
 *   - 기타 모든 API
 *
 * 📦 메모리 저장소:
 *   - pendingMessages: topicId 생성 전 임시 저장 (개요 대화)
 *   - mockTopicMessages: topicId별 전체 메시지 (생성 후)
 *
 * 🔄 플로우:
 *   1. POST /api/outlines/ask → pendingMessages에 User/Assistant 저장
 *   2. "예" 클릭 → POST /api/topics/generate (Real API)
 *   3. GET /api/topics/:id/messages → pendingMessages + 최종 보고서 반환
 *
 * 📝 새로운 Mock API 추가 방법:
 *   handlers 배열에 http.get() 또는 http.post() 추가
 *
 * @see https://mswjs.io/docs/
 */

export interface OutlineRequest {
    id: number // 0, 1, 2, 3... 순차적 번호
    message: string
}

export interface OutlineResponse {
    id: number // 클라이언트가 보낸 ID 그대로 반환
    outline: string
    timestamp: number
}

/**
 * Mock API 목록을 반환하는 헬퍼 함수
 * 개발 중 어떤 API가 mock되는지 확인할 때 사용
 */
export function getMockedEndpoints(): string[] {
    return handlers.map((handler) => {
        // MSW handler에서 URL 패턴 추출
        const info = handler.info
        return `${info.method} ${info.path}`
    })
}

/**
 * 특정 URL이 mock 처리되는지 확인
 */
export function isMockedEndpoint(method: string, url: string): boolean {
    const endpoints = getMockedEndpoints()
    return endpoints.some((endpoint) => {
        const [m, path] = endpoint.split(' ')
        return m === method && url.includes(path)
    })
}

// Mock 데이터 저장소 (메모리)
const mockTopicMessages = new Map<number, any[]>()

// 프론트엔드 스토어 참조 (window 객체를 통해)
function getFrontendMessages(topicId: number): any[] {
    // @ts-ignore
    const store = window.__messageStore
    if (store && store.getState) {
        const state = store.getState()
        const messages = state.messagesByTopic.get(topicId)
        return messages || []
    }
    return []
}

// 전체 메시지 저장소 (topicId 생성 전 임시 저장)
interface PendingMessage {
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    seqNo: number
}
// topicId별로 pending 메시지를 관리 (여러 대화를 동시 테스트 가능)
const pendingMessagesByTopic = new Map<number, PendingMessage[]>()
let tempTopicIdCounter = 0 // 임시 topicId (음수로 관리)

// tempTopicId → realTopicId 매핑
const topicIdMapping = new Map<number, number>()
let lastTempTopicId: number | null = null // 가장 최근 tempTopicId

// 개요 메시지 ID counter (임시 음수 ID)
let tempMessageIdCounter = -1

// 개발 환경에서 디버깅용으로 window 객체에 노출
if (typeof window !== 'undefined') {
    // @ts-ignore
    window.mockTopicMessages = mockTopicMessages
    // @ts-ignore
    window.pendingMessagesByTopic = pendingMessagesByTopic
    // @ts-ignore
    window.topicIdMapping = topicIdMapping
    // @ts-ignore
    window.clearPendingMessages = () => {
        pendingMessagesByTopic.clear()
        topicIdMapping.clear()
        lastTempTopicId = null
        tempTopicIdCounter = 0
        tempMessageIdCounter = -1
        console.log('✅ Pending messages cleared')
    }
}

export const handlers = [
    /**
     * Mock: 개요 생성 API
     * POST /api/outlines/ask
     *
     * 테스트 전략:
     * - outline 메시지는 현재 DB에 저장되지 않음 (backend 미구현)
     * - 임시 topicId(음수)로 pendingMessagesByTopic에 저장
     * - generateTopic 호출 시 실제 topicId로 변환
     */
    http.post<never, OutlineRequest>('http://localhost:8000/api/outlines/ask', async ({request}) => {
        const body = await request.json()

        // 500ms ~ 1500ms 지연 시뮬레이션
        await delay(500 + Math.random() * 1000)

        // 임시 topicId (첫 요청이면 생성)
        const tempTopicId = body.id === 0 ? --tempTopicIdCounter : body.id

        if (!pendingMessagesByTopic.has(tempTopicId)) {
            pendingMessagesByTopic.set(tempTopicId, [])
        }

        const messages = pendingMessagesByTopic.get(tempTopicId)!

        // User 메시지 저장 (seqNo 기반)
        const userSeqNo = messages.length
        messages.push({
            role: 'user',
            content: body.message,
            timestamp: new Date().toISOString(),
            seqNo: userSeqNo
        })

        // Mock 개요 생성
        let outline = `**주제 이해**
`
        outline += `"${body.message}"에 대한 보고서를 작성하겠습니다.

`
        outline += `**주요 포함 내용**
`
        outline += `- 배경 및 현황 분석
`
        outline += `- 핵심 데이터 및 통계
`
        outline += `- 전문가 의견 및 시사점

`
        outline += `이 내용으로 진행하시겠습니까?`

        // ✅ Assistant 개요 응답 저장
        const assistantSeqNo = messages.length
        messages.push({
            role: 'assistant',
            content: outline,
            timestamp: new Date(Date.now() + 1000).toISOString(),
            seqNo: assistantSeqNo
        })

        // lastTempTopicId 저장
        lastTempTopicId = tempTopicId

        console.log(`[MSW] Outline request - tempTopicId: ${tempTopicId}, messages count: ${messages.length}`)

        return HttpResponse.json<OutlineResponse>({
            id: tempTopicId,
            outline,
            timestamp: Date.now()
        })
    }),

    /**
     * Mock: 메시지 목록 조회 (개요 메시지 포함 시뮬레이션)
     * GET /api/topics/:topicId/messages
     *
     * 테스트 전략:
     * - generateTopic으로 생성된 topicId는 실제 백엔드에서 옴
     * - 해당 topicId의 메시지 조회 시:
     *   1. pendingMessages에서 임시 저장된 outline 메시지 가져오기
     *   2. 실제 backend 메시지와 합치기
     * - 현재는 backend 미구현이므로 pending만 반환
     */
    http.get('http://localhost:8000/api/topics/:topicId/messages', async ({params}) => {
        const topicId = Number(params.topicId)

        // 500ms 지연 시뮬레이션
        await delay(500)

        // Mock 메시지가 없으면 생성
        if (!mockTopicMessages.has(topicId)) {
            const messages: any[] = []
            let messageIdCounter = 1

            // ✅ 프론트엔드 스토어에서 임시 메시지 가져오기
            let tempTopicIdForThisReal: number | null = null
            for (const [tempId, realId] of topicIdMapping.entries()) {
                if (realId === topicId) {
                    tempTopicIdForThisReal = tempId
                    break
                }
            }

            // 프론트엔드 스토어에서 임시 메시지 조회
            const frontendMessages = tempTopicIdForThisReal ? getFrontendMessages(tempTopicIdForThisReal) : []

            console.log(
                `[MSW] Messages fetch - realTopicId: ${topicId}, tempTopicId: ${tempTopicIdForThisReal}, frontend messages count: ${frontendMessages?.length || 0}`
            )

            if (frontendMessages && frontendMessages.length > 0) {
                // 프론트엔드 메시지를 백엔드 형식으로 변환
                frontendMessages.forEach((msg: any) => {
                    messages.push({
                        id: messageIdCounter++,
                        topic_id: topicId, // 실제 topicId로 변환
                        role: msg.role,
                        content: msg.content,
                        seq_no: msg.seqNo,
                        created_at: msg.createdAt,
                        updated_at: msg.createdAt
                    })
                })

                // ✅ 임시 topicId 매핑 삭제 (더 이상 필요 없음)
                if (tempTopicIdForThisReal) {
                    topicIdMapping.delete(tempTopicIdForThisReal)
                }
            } else {
                // 저장된 메시지가 없으면 기본 메시지
                messages.push({
                    id: messageIdCounter++,
                    topic_id: topicId,
                    role: 'user',
                    content: '디지털뱅킹 트렌드 보고서 작성해줘',
                    seq_no: 0,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                })
            }

            mockTopicMessages.set(topicId, messages)
            console.log(`[MSW] Messages fetched for topicId: ${topicId}, count: ${messages.length}`)
        }

        return HttpResponse.json({
            success: true,
            data: {
                messages: mockTopicMessages.get(topicId),
                total: mockTopicMessages.get(topicId)?.length || 0
            },
            error: null,
            meta: {
                requestId: `mock-${Date.now()}`
            }
        })
    }),

    /**
     * Mock: 보고서 생성 API
     * POST /api/topics/generate
     *
     * 테스트 전략:
     * - 실제 topicId 생성 (양수)
     * - pending 메시지와 연결
     */
    http.post('http://localhost:8000/api/topics/generate', async ({request}) => {
        const body = (await request.json()) as {input_prompt: string; language: string}

        // 1~2초 지연 시뮬레이션
        await delay(1000 + Math.random() * 1000)

        // 실제 topicId 생성 (양수)
        const realTopicId = Date.now() % 100000 // 간단한 ID 생성

        // tempTopicId → realTopicId 매핑 저장
        if (lastTempTopicId !== null) {
            topicIdMapping.set(lastTempTopicId, realTopicId)
            console.log(`[MSW] Topic mapping - tempTopicId: ${lastTempTopicId} → realTopicId: ${realTopicId}`)
        }

        console.log(`[MSW] Topic generated - realTopicId: ${realTopicId}`)

        return HttpResponse.json({
            success: true,
            data: {
                topic_id: realTopicId,
                title: '보고서 주제',
                artifacts: [
                    {
                        artifact_id: 1,
                        type: 'markdown',
                        filename: 'report.md',
                        content: `# 생성된 보고서

보고서 내용...`
                    }
                ]
            },
            error: null,
            meta: {
                requestId: `mock-${Date.now()}`
            }
        })
    }),

    /**
     * Mock: 토픽별 아티팩트 목록 조회
     * GET /api/artifacts/topics/:topicId
     *
     * 테스트 전략:
     * - generateTopic으로 생성된 topicId에 대한 아티팩트 반환
     * - 기본적으로 1개의 MD 아티팩트 반환
     */
    http.get('http://localhost:8000/api/artifacts/topics/:topicId', async ({params}) => {
        const topicId = Number(params.topicId)

        // 300ms 지연 시뮬레이션
        await delay(300)

        // Mock 아티팩트 데이터
        const mockArtifact = {
            id: 1,
            topic_id: topicId,
            message_id: 2, // 최종 보고서 메시지 ID
            kind: 'md' as const,
            locale: 'ko',
            version: 1,
            filename: `report_topic_${topicId}.md`,
            file_path: `/artifacts/report_topic_${topicId}.md`,
            file_size: 2048,
            sha256: 'mock-sha256-hash-' + topicId,
            created_at: new Date().toISOString()
        }

        console.log(`[MSW] Artifacts fetched for topicId: ${topicId}`)

        return HttpResponse.json({
            success: true,
            data: {
                artifacts: [mockArtifact],
                total: 1,
                topic_id: topicId
            },
            error: null,
            meta: {
                requestId: `req_artifact_${Date.now()}`
            },
            feedback: []
        })
    }),

    /**
     * Mock: 아티팩트 내용 조회
     * GET /api/artifacts/:artifactId/content
     *
     * 테스트 전략:
     * - MD 파일의 실제 내용을 반환
     * - 다양한 섹션을 포함한 완전한 보고서 내용 시뮬레이션
     */
    http.get('http://localhost:8000/api/artifacts/:artifactId/content', async ({params}) => {
        const artifactId = Number(params.artifactId)

        // 200ms 지연 시뮬레이션
        await delay(200)

        // Mock 보고서 내용
        const mockContent = `# 디지털뱅킹 트렌드 분석 보고서

## 요약

최근 디지털뱅킹 시장은 모바일 중심의 혁신적인 변화를 겪고 있습니다. 본 보고서는 2024-2025년 디지털뱅킹의 주요 트렌드와 시장 전망을 분석합니다.

**핵심 내용:**
- 모바일 뱅킹 사용자 증가율: 전년 대비 32%
- AI 기반 개인화 서비스 확대
- 오픈뱅킹 API 생태계 성장

## 배경

디지털 전환이 가속화되면서 금융 서비스의 패러다임이 변화하고 있습니다. 특히 MZ세대를 중심으로 비대면 금융 서비스 선호도가 급증하고 있으며, 이에 따라 전통적인 은행들도 디지털 혁신에 적극 투자하고 있습니다.

### 시장 현황

- 국내 인터넷전문은행 고객 수: 2,500만 명 돌파
- 모바일뱅킹 거래액: 연간 1,200조 원 규모
- 디지털 채널 이용률: 전체 거래의 85% 이상

## 주요 내용

### 1. AI 기반 개인화 서비스

인공지능을 활용한 맞춤형 금융 상품 추천과 자산 관리 서비스가 확대되고 있습니다.

**주요 사례:**
- 챗봇 기반 24시간 고객 상담
- AI 투자 자문 서비스
- 소비 패턴 분석을 통한 재무 관리

### 2. 오픈뱅킹 생태계

오픈API를 통한 금융 데이터 공유로 핀테크 기업과의 협업이 활발해지고 있습니다.

### 3. 보안 강화

생체 인증, 블록체인 등 첨단 기술을 활용한 보안 시스템이 도입되고 있습니다.

## 결론

디지털뱅킹은 더 이상 선택이 아닌 필수가 되었습니다. 향후 금융 기관들은 고객 경험 개선과 보안 강화에 중점을 두어야 하며, 핀테크 기업과의 협업을 통해 혁신적인 서비스를 제공해야 할 것입니다.

### 향후 추진 방향

1. AI/ML 기술 투자 확대
2. 디지털 접근성 개선
3. 금융 포용성 강화
4. 규제 대응 체계 구축`

        console.log(`[MSW] Artifact content fetched for artifactId: ${artifactId}`)

        return HttpResponse.json({
            success: true,
            data: {
                artifact_id: artifactId,
                content: mockContent,
                filename: `report_v${artifactId}.md`,
                kind: 'md' as const
            },
            error: null,
            meta: {
                requestId: `req_content_${Date.now()}`
            },
            feedback: []
        })
    })
]
