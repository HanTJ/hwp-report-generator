/**
 * artifact.ts
 *
 * 아티팩트(산출물) 관련 TypeScript 타입 정의
 */

export type ArtifactKind = 'md' | 'hwpx'

// 아티팩트
export interface Artifact {
    id: number
    topic_id: number
    message_id: number | null
    kind: ArtifactKind
    locale: string | null
    version: number
    filename: string
    file_path: string
    file_size: number
    sha256: string | null
    created_at: string
    content?: string
}

// 아티팩트 목록 응답
export interface ArtifactListResponse {
    artifacts: Artifact[]
    total: number
    topic_id: number
}

// 아티팩트 내용 응답 (MD 파일만)
export interface ArtifactContentResponse {
    artifact_id: number
    content: string
    filename: string
    kind: ArtifactKind
}
