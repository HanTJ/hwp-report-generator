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
