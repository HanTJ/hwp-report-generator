/**
 * topicApi.ts
 *
 * 토픽(대화 스레드) 관련 API 함수 모음
 */

import api from "./api";
import { API_ENDPOINTS } from "../constants/";
import type {
  TopicCreate,
  TopicUpdate,
  Topic,
  TopicListResponse,
} from "../types/topic";
import type { ApiResponse } from "../types/api";

export const topicApi = {
  /**
   * 새 토픽 생성
   * POST /api/topics
   * @param data 토픽 생성 데이터
   * @returns 생성된 토픽
   */
  createTopic: async (data: TopicCreate): Promise<Topic> => {
    const response = await api.post<ApiResponse<Topic>>(
      API_ENDPOINTS.CREATE_TOPIC,
      data
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(
        response.data.error?.message || "토픽 생성에 실패했습니다."
      );
    }

    return response.data.data;
  },

  /**
   * 토픽 목록 조회
   * GET /api/topics
   * @param status 토픽 상태 필터 (optional)
   * @param page 페이지 번호
   * @param pageSize 페이지 크기
   * @returns 토픽 목록
   */
  listTopics: async (
    status?: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<TopicListResponse> => {
    const params = new URLSearchParams();
    if (status) params.append("status", status);
    params.append("page", page.toString());
    params.append("page_size", pageSize.toString());

    const response = await api.get<ApiResponse<TopicListResponse>>(
      `${API_ENDPOINTS.LIST_TOPICS}?${params.toString()}`
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(
        response.data.error?.message || "토픽 목록 조회에 실패했습니다."
      );
    }

    return response.data.data;
  },

  /**
   * 특정 토픽 조회
   * GET /api/topics/{topicId}
   * @param topicId 토픽 ID
   * @returns 토픽 정보
   */
  getTopic: async (topicId: number): Promise<Topic> => {
    const response = await api.get<ApiResponse<Topic>>(
      API_ENDPOINTS.GET_TOPIC(topicId)
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(
        response.data.error?.message || "토픽 조회에 실패했습니다."
      );
    }

    return response.data.data;
  },

  /**
   * 토픽 업데이트
   * PATCH /api/topics/{topicId}
   * @param topicId 토픽 ID
   * @param data 업데이트 데이터
   * @returns 업데이트된 토픽
   */
  updateTopic: async (topicId: number, data: TopicUpdate): Promise<Topic> => {
    const response = await api.patch<ApiResponse<Topic>>(
      API_ENDPOINTS.UPDATE_TOPIC(topicId),
      data
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(
        response.data.error?.message || "토픽 업데이트에 실패했습니다."
      );
    }

    return response.data.data;
  },

  /**
   * 토픽 삭제
   * DELETE /api/topics/{topicId}
   * @param topicId 토픽 ID
   */
  deleteTopic: async (topicId: number): Promise<void> => {
    const response = await api.delete<ApiResponse<void>>(
      API_ENDPOINTS.DELETE_TOPIC(topicId)
    );

    if (!response.data.success) {
      throw new Error(
        response.data.error?.message || "토픽 삭제에 실패했습니다."
      );
    }
  },
};
