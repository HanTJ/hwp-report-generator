/**
 * topic.ts
 *
 * 토픽(대화 스레드) 관련 TypeScript 타입 정의
 */

export type TopicStatus = "active" | "archived" | "deleted";

export interface TopicCreate {
  input_prompt: string;
  language?: string;
}

export interface TopicUpdate {
  generated_title?: string;
  status?: TopicStatus;
}

export interface Topic {
  id: number;
  input_prompt: string;
  generated_title: string | null;
  language: string;
  status: TopicStatus;
  created_at: string;
  updated_at: string;
}

export interface TopicListResponse {
  topics: Topic[];
  total: number;
  page: number;
  page_size: number;
}

// Ask API Request
export interface AskRequest {
  content: string;
  artifact_id?: number | null;
  include_artifact_content?: boolean;
  max_messages?: number | null;
  system_prompt?: string | null;
}

// Ask API Response
export interface AskResponse {
  topic_id: number;
  user_message: {
    id: number;
    topic_id: number;
    role: string;
    content: string;
    seq_no: number;
    created_at: string;
  };
  assistant_message: {
    id: number;
    topic_id: number;
    role: string;
    content: string;
    seq_no: number;
    created_at: string;
  };
  artifact: {
    id: number;
    kind: string;
    filename: string;
    file_path: string;
    file_size: number;
    version: number;
    created_at: string;
  };
  usage: {
    model: string;
    input_tokens: number;
    output_tokens: number;
    latency_ms: number;
  };
}
