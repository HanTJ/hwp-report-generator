import {http, HttpResponse, delay} from 'msw'

/**
 * MSW Mock API 핸들러
 *
 * 🔵 Mock 처리되는 API (MSW intercept):
 *   - POST /api/topics/plan - 보고서 작성 계획 생성 (첫 메시지)
 *   - POST /api/topics/generate - 보고서 생성 ("예" 클릭 시)
 *   - GET /api/artifacts/topics/:topicId - 토픽별 아티팩트 목록 조회
 *   - GET /api/artifacts/:artifactId/content - 아티팩트 내용 조회 (MD)
 *
 * 📦 메모리 저장소:
 *   - mockTopicMessages: topicId별 전체 메시지
 *
 * 🔄 플로우:
 *   1. 첫 메시지 입력 → POST /api/topics/plan → 계획 생성 (Zustand 저장)
 *   2. "예" 클릭 → POST /api/topics/generate → 실제 보고서 생성
 *   3. GET /api/topics/:id/messages → 메시지 조회 (DB에서)
 *
 * 📝 새로운 Mock API 추가 방법:
 *   handlers 배열에 http.get() 또는 http.post() 추가
 *
 * @see https://mswjs.io/docs/
 */

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

export const handlers = [
    /**
     * Mock: 보고서 작성 계획 생성 API
     * POST /api/topics/plan
     *
     * 테스트 전략:
     * - 임시 topicId 생성 (음수)
     * - 계획(plan)과 섹션 목록 반환
     * - 첫 메시지 입력 시 호출됨
     */
    http.post('http://localhost:8000/api/topics/plan', async ({request}) => {
        const body = (await request.json()) as {template_id?: number; topic?: string}

        // 1~2초 지연 시뮬레이션 (AI 응답 시뮬레이션)
        await delay(1000 + Math.random() * 1000)

        // topic_id 생성
        const topicId = Date.now() // 간단한 임시 ID 생성

        // Mock 계획 내용 생성
        const mockPlan = `# ${body.topic || '보고서 주제'} 작성 계획

이 보고서는 다음과 같은 구조로 작성됩니다:

## 1. 요약
- 핵심 내용을 간단히 정리합니다
- 주요 발견사항과 결론을 제시합니다

## 2. 배경 및 목적
- 보고서 작성의 배경을 설명합니다
- 분석 목적과 범위를 명확히 합니다

## 3. 주요 내용
- 상세한 분석 결과를 제시합니다
- 데이터와 근거를 바탕으로 설명합니다

## 4. 결론 및 제언
- 분석 결과를 종합합니다
- 향후 방향성과 실행 계획을 제안합니다`

        const mockSections = [
            {
                title: '요약',
                description: '보고서의 핵심 내용과 주요 발견사항'
            },
            {
                title: '배경 및 목적',
                description: '보고서 작성 배경과 분석 목적'
            },
            {
                title: '주요 내용',
                description: '상세 분석 결과 및 데이터'
            },
            {
                title: '결론 및 제언',
                description: '종합 결론과 향후 방향성'
            }
        ]

        console.log(`[MSW] Plan generated - topicId: ${topicId}, topic: ${body.topic}`)

        return HttpResponse.json({
            success: true,
            data: {
                topic_id: topicId,
                plan: mockPlan,
                sections: mockSections
            },
            error: null,
            meta: {
                requestId: `mock-plan-${Date.now()}`
            },
            feedback: []
        })
    }),

    /**
     * Mock: 보고서 생성 API (백그라운드)
     * POST /api/topics/:topicId/generate
     *
     * 테스트 전략:
     * - 즉시 202 Accepted 반환 (< 1초)
     * - 백그라운드에서 보고서 생성 시뮬레이션
     * - status_check_url 제공
     */
    http.post('http://localhost:8000/api/topics/:topicId/generate', async ({request, params}) => {
        const topicId = Number(params.topicId)
        const body = (await request.json()) as {topic: string; plan: string; template_id?: number}

        // 짧은 지연 (< 1초)
        await delay(500)

        console.log(`[MSW] Report generation started - topicId: ${topicId}, topic: ${body.topic}`)

        // 백그라운드 생성 시뮬레이션 (3초 후 완료로 가정)
        setTimeout(() => {
            console.log(`[MSW] Report generation completed - topicId: ${topicId}`)
            // 실제로는 GET /api/topics/:topicId/status에서 completed 상태 반환
        }, 3000)

        return HttpResponse.json(
            {
                success: true,
                data: {
                    topic_id: topicId,
                    status: 'generating',
                    message: 'Report generation started in background',
                    status_check_url: `/api/topics/${topicId}/status`
                },
                error: null,
                meta: {
                    requestId: `mock-generate-${Date.now()}`
                },
                feedback: []
            },
            {status: 202}
        )
    }),

    /**
     * Mock: 보고서 생성 상태 조회 API
     * GET /api/topics/:topicId/status
     *
     * 테스트 전략:
     * - 진행 상황 반환 (폴링용)
     * - 3초 후 completed 상태로 변경
     */
    http.get('http://localhost:8000/api/topics/:topicId/status', async ({params}) => {
        const topicId = Number(params.topicId)

        // 짧은 지연
        await delay(200)

        // 간단한 시뮬레이션: 항상 완료 상태 반환
        // 실제로는 생성 시작 시간을 추적하여 진행률 계산
        console.log(`[MSW] Status check - topicId: ${topicId}`)

        return HttpResponse.json({
            success: true,
            data: {
                topic_id: topicId,
                status: 'completed', // 'generating', 'completed', 'failed'
                progress_percent: 100,
                current_step: '보고서 생성 완료',
                artifact_id: 1,
                started_at: new Date(Date.now() - 3000).toISOString(),
                completed_at: new Date().toISOString()
            },
            error: null,
            meta: {
                requestId: `mock-status-${Date.now()}`
            },
            feedback: []
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
            message_id: 1, // Backend 메시지 ID (seq_no 3에 해당)
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
    }),
    /**
     * Mock: 토픽의 메시지 목록 조회 API
     * GET /api/topics/:topicId/messages
     *
     * 테스트 전략:
     * - 보고서 생성 완료 후 호출됨
     * - 사용자 메시지(seq_no:3) + AI 응답 메시지(seq_no:4) 반환
     */
    http.get('http://localhost:8000/api/topics/:topicId/messages', async ({params}) => {
        const topicId = Number(params.topicId)
        console.log(`[MSW] Fetching messages for topicId: ${topicId}`)

        // 짧은 지연
        await delay(200)

        // Mock 메시지 목록 (보고서 생성 후)
        // seq_no: 1,2는 계획 모드에서 이미 사용 (클라이언트 전용, id: undefined)
        // seq_no: 3는 보고서 생성 후 Backend에서 생성된 메시지 (artifact 포함)
        const mockMessages = [
            {
                id: 1,
                topic_id: topicId,
                role: 'assistant' as const,
                content: '# 보고서 제목\n\n보고서 내용이 여기에 표시됩니다.',
                seq_no: 3, // seq_no 1,2는 계획 메시지가 사용
                created_at: new Date().toISOString()
            }
        ]

        console.log(`[MSW] Messages fetched for topicId: ${topicId}, count: ${mockMessages.length}`)

        return HttpResponse.json({
            success: true,
            data: {
                messages: mockMessages,
                total: mockMessages.length,
                topic_id: topicId
            },
            error: null,
            meta: {
                requestId: `mock-messages-${Date.now()}`
            },
            feedback: []
        })
    }),

    /**
     * Mock: 템플릿 상세 조회 API
     * GET /api/templates/:templateId
     *
     * 테스트 전략:
     * - prompt_user, prompt_system 필드 포함
     * - 플레이스홀더 목록 반환
     */
    http.get('http://localhost:8000/api/templates/:templateId', async ({params}) => {
        const templateId = Number(params.templateId)

        await delay(200)

        const mockTemplate = {
            id: templateId,
            title: '재무보고서 템플릿',
            filename: 'financial_report.hwpx',
            file_size: 45678,
            placeholders: [{key: '{{TITLE}}'}, {key: '{{SUMMARY}}'}, {key: '{{CONTENT}}'}],
            prompt_user: '간결하고 명확하게 작성하세요',
            prompt_system: '당신은 전문 금융 보고서 작성 AI입니다. 정확한 데이터 분석과 명확한 표현을 사용하세요.',
            created_at: new Date().toISOString()
        }

        console.log(`[MSW] Template detail fetched - templateId: ${templateId}`)

        return HttpResponse.json({
            success: true,
            data: mockTemplate,
            error: null,
            meta: {
                requestId: `mock-template-${Date.now()}`
            },
            feedback: []
        })
    }),

    /**
     * Mock: User Prompt 업데이트 API
     * PUT /api/templates/:templateId/prompt-user
     */
    http.put('http://localhost:8000/api/templates/:templateId/prompt-user', async ({request, params}) => {
        const templateId = Number(params.templateId)
        const body = (await request.json()) as {prompt_user: string}

        await delay(300)

        console.log(`[MSW] User prompt updated - templateId: ${templateId}, prompt: ${body.prompt_user}`)

        return HttpResponse.json({
            success: true,
            data: {
                id: templateId,
                title: '재무보고서 템플릿',
                prompt_user: body.prompt_user,
                prompt_system: '당신은 전문 금융 보고서 작성 AI입니다.',
                updated_at: new Date().toISOString()
            },
            error: null,
            meta: {
                requestId: `mock-update-user-${Date.now()}`
            },
            feedback: []
        })
    }),

    /**
     * Mock: System Prompt 업데이트 API
     * PUT /api/templates/:templateId/prompt-system
     */
    http.put('http://localhost:8000/api/templates/:templateId/prompt-system', async ({request, params}) => {
        const templateId = Number(params.templateId)
        const body = (await request.json()) as {prompt_system: string}

        await delay(300)

        console.log(`[MSW] System prompt updated - templateId: ${templateId}`)

        return HttpResponse.json({
            success: true,
            data: {
                id: templateId,
                title: '재무보고서 템플릿',
                prompt_user: '간결하고 명확하게 작성하세요',
                prompt_system: body.prompt_system,
                updated_at: new Date().toISOString()
            },
            error: null,
            meta: {
                requestId: `mock-update-system-${Date.now()}`
            },
            feedback: []
        })
    }),

    /**
     * Mock: System Prompt 재생성 API
     * POST /api/templates/:templateId/regenerate-prompt-system
     */
    http.post('http://localhost:8000/api/templates/:templateId/regenerate-prompt-system', async ({params}) => {
        const templateId = Number(params.templateId)

        await delay(500)

        const regeneratedPrompt =
            '당신은 전문 금융 보고서 작성 AI입니다. 다음 플레이스홀더를 채워 완전한 보고서를 작성하세요:\n\n- {{TITLE}}: 보고서 제목\n- {{SUMMARY}}: 핵심 요약\n- {{CONTENT}}: 상세 내용\n\n정확한 데이터 분석과 명확한 표현을 사용하여 전문성 있는 보고서를 작성하세요.'

        console.log(`[MSW] System prompt regenerated - templateId: ${templateId}`)

        return HttpResponse.json({
            success: true,
            data: {
                id: templateId,
                prompt_system: regeneratedPrompt,
                regenerated_at: new Date().toISOString()
            },
            error: null,
            meta: {
                requestId: `mock-regenerate-${Date.now()}`
            },
            feedback: []
        })
    }),

    /**
     * Mock: 템플릿 목록 조회 API
     * GET /api/templates
     */
    http.get('http://localhost:8000/api/templates', async () => {
        await delay(200)

        const mockTemplates = [
            {
                id: 1,
                title: '재무보고서 템플릿',
                filename: 'financial_report.hwpx',
                file_size: 45678,
                created_at: new Date(Date.now() - 86400000).toISOString()
            },
            {
                id: 2,
                title: '영업보고서 템플릿',
                filename: 'sales_report.hwpx',
                file_size: 52341,
                created_at: new Date(Date.now() - 172800000).toISOString()
            }
        ]

        console.log(`[MSW] Template list fetched - count: ${mockTemplates.length}`)

        return HttpResponse.json({
            success: true,
            data: mockTemplates,
            error: null,
            meta: {
                requestId: `mock-templates-${Date.now()}`
            },
            feedback: []
        })
    }),

    /**
     * Mock: 템플릿 삭제 API
     * DELETE /api/templates/:templateId
     */
    http.delete('http://localhost:8000/api/templates/:templateId', async ({params}) => {
        const templateId = Number(params.templateId)

        await delay(300)

        console.log(`[MSW] Template deleted - templateId: ${templateId}`)

        return HttpResponse.json({
            success: true,
            data: {
                id: templateId,
                message: '템플릿이 삭제되었습니다.'
            },
            error: null,
            meta: {
                requestId: `mock-delete-${Date.now()}`
            },
            feedback: []
        })
    })
]
