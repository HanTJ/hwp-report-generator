/**
 * artifactApi.ts
 *
 * 아티팩트(산출물) 관련 API 함수 모음
 */

import api from "./api";
import { API_ENDPOINTS, API_BASE_URL } from "../constants/";
import type {
  Artifact,
  ArtifactListResponse,
  ArtifactContentResponse,
  ArtifactKind,
} from "../types/artifact";
import type { ApiResponse } from "../types/api";

export const artifactApi = {
  /**
   * 아티팩트 메타데이터 조회
   * GET /api/artifacts/{artifactId}
   * @param artifactId 아티팩트 ID
   * @returns 아티팩트 정보
   */
  getArtifact: async (artifactId: number): Promise<Artifact> => {
    const response = await api.get<ApiResponse<Artifact>>(
      API_ENDPOINTS.GET_ARTIFACT(artifactId)
    );

    if (!response.data.success || !response.data.data) {
      console.log("getArtifact > failed >", response.data);

      throw new Error(
        response.data.error?.message || "아티팩트 조회에 실패했습니다."
      );
    }

    console.log("getArtifact > success >", response.data);

    return response.data.data;
  },

  /**
   * MD 파일 내용 조회
   * GET /api/artifacts/{artifactId}/content
   * @param artifactId 아티팩트 ID
   * @returns MD 파일 내용
   */
  getArtifactContent: async (
    artifactId: number
  ): Promise<ArtifactContentResponse> => {
    const response = await api.get<ApiResponse<ArtifactContentResponse>>(
      API_ENDPOINTS.GET_ARTIFACT_CONTENT(artifactId)
    );

    if (!response.data.success || !response.data.data) {
      console.log("getArtifactContent > failed >", response.data);

      throw new Error(
        response.data.error?.message || "파일 내용 조회에 실패했습니다."
      );
    }

    console.log("getArtifactContent > success >", response.data);

    return response.data.data;
  },

  /**
   * 파일 다운로드 (브라우저에서 다운로드 트리거)
   * GET /api/artifacts/{artifactId}/download
   * @param artifactId 아티팩트 ID
   * @param fallbackFilename 파일명 추출 실패 시 사용할 기본 파일명 (optional)
   */
  downloadArtifact: async (
    artifactId: number,
    fallbackFilename?: string
  ): Promise<void> => {
    const token = localStorage.getItem("access_token");
    const url = `${API_BASE_URL}${API_ENDPOINTS.DOWNLOAD_ARTIFACT(artifactId)}`;

    try {
      // Authorization 헤더를 포함한 다운로드를 위해 fetch 사용
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.log("downloadArtifact > failed >", response);

        throw new Error("파일 다운로드에 실패했습니다.");
      }

      const blob = await response.blob();

      // 파일명 추출 (Content-Disposition 헤더에서)
      const contentDisposition = response.headers.get("content-disposition");
      let filename = fallbackFilename || `artifact_${artifactId}.md`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(
          /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
        );
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, "");
        }
      }

      // Blob을 다운로드
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.log("downloadArtifact > failed >", error);

      throw new Error("파일 다운로드에 실패했습니다.");
    }
  },

  /**
   * 토픽의 아티팩트 목록 조회
   * GET /api/artifacts/topics/{topicId}
   * @param topicId 토픽 ID
   * @param kind 아티팩트 종류 필터 (optional)
   * @param locale 언어 필터 (optional)
   * @param page 페이지 번호
   * @param pageSize 페이지 크기
   * @returns 아티팩트 목록
   */
  listArtifactsByTopic: async (
    topicId: number,
    kind?: ArtifactKind,
    locale?: string,
    page: number = 1,
    pageSize: number = 50
  ): Promise<ArtifactListResponse> => {
    const params = new URLSearchParams();
    if (kind) params.append("kind", kind);
    if (locale) params.append("locale", locale);
    params.append("page", page.toString());
    params.append("page_size", pageSize.toString());

    const response = await api.get<ApiResponse<ArtifactListResponse>>(
      `${API_ENDPOINTS.LIST_ARTIFACTS_BY_TOPIC(topicId)}?${params.toString()}`
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(
        response.data.error?.message || "아티팩트 목록 조회에 실패했습니다."
      );
    }

    return response.data.data;
  },

  /**
   * MD 파일을 HWPX로 변환
   * POST /api/artifacts/{artifactId}/convert
   * @param artifactId 소스 MD 아티팩트 ID
   * @returns 생성된 HWPX 아티팩트
   */
  convertToHwpx: async (artifactId: number): Promise<Artifact> => {
    const response = await api.post<ApiResponse<Artifact>>(
      API_ENDPOINTS.CONVERT_ARTIFACT(artifactId)
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(
        response.data.error?.message || "파일 변환에 실패했습니다."
      );
    }

    return response.data.data;
  },

  /**
   * 메시지 기반 HWPX 다운로드
   * GET /api/artifacts/messages/{messageId}/hwpx/download
   * @param messageId 메시지 ID
   * @param filename 다운로드할 파일명
   * @param locale 언어 (기본값: ko)
   */
  downloadMessageHwpx: async (
    messageId: number,
    filename: string,
    locale: string = "ko"
  ): Promise<void> => {
    const token = localStorage.getItem("access_token");
    const url = `${API_BASE_URL}${API_ENDPOINTS.DOWNLOAD_MESSAGE_HWPX(
      messageId,
      locale
    )}`;

    try {
      // Authorization 헤더를 포함한 다운로드를 위해 fetch 사용
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.log("downloadMessageHwpx > failed >", response);

        throw new Error("파일 다운로드에 실패했습니다.");
      }

      const blob = await response.blob();

      // Blob을 다운로드
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.log("downloadMessageHwpx > failed >", error);

      throw new Error("파일 다운로드에 실패했습니다.");
    }
  },
};
