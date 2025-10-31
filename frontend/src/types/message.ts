/**
 * message.ts
 *
 * 메시지 관련 TypeScript 타입 정의
 */

export type MessageRole = 'user' | 'assistant' | 'system';

// 메시지
export interface Message {
  id: number;
  topic_id: number;
  user_id: number | null;
  role: MessageRole;
  content: string;
  seq_no: number;
  created_at: string;
}

// 메시지 목록 응답
export interface MessageListResponse {
  messages: Message[];
  total: number;
  topic_id: number;
}

// 새 메시지 생성 요청 (토픽 내)
export interface CreateMessageRequest {
  role: MessageRole;
  content: string;
}
