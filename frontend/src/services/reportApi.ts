import api from "./api";
import { API_ENDPOINTS } from "../constants/";
import type {
  ReportRequest,
  ReportResponse,
  ReportListResponse,
} from "../types/report";
import type { ApiResponse } from "../types/api";

export const reportApi = {
  generateReport: async (data: ReportRequest): Promise<ReportResponse> => {
    const response = await api.post<ApiResponse<ReportResponse>>(
      API_ENDPOINTS.GENERATE_REPORT,
      data
    );

    if (!response.data.success || !response.data.data) {
      console.log("generateReport > failed >", response.data.error);

      throw new Error(
        response.data.error?.message || "보고서 생성에 실패했습니다."
      );
    }

    console.log("generateReport > success >", response.data);

    return response.data.data;
  },

  listReports: async (): Promise<ReportListResponse> => {
    const response = await api.get<ApiResponse<ReportListResponse>>(
      API_ENDPOINTS.LIST_REPORTS
    );

    if (!response.data.success || !response.data.data) {
      console.log("listReports > failed >", response.data);

      throw new Error(
        response.data.error?.message || "보고서 목록 조회에 실패했습니다."
      );
    }

    console.log("listReports > success >", response.data);

    return response.data.data;
  },

  downloadReport: (filename: string): string => {
    return `${API_ENDPOINTS.DOWNLOAD_REPORT(filename)}`;
  },
};
