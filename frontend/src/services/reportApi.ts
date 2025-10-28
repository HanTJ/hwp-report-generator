import api from './api';
import { API_ENDPOINTS } from '../constants/';
import type { ReportRequest, ReportResponse, ReportListResponse } from '../types/report';

export const reportApi = {
  generateReport: async (data: ReportRequest): Promise<ReportResponse> => {
    const response = await api.post<ReportResponse>(API_ENDPOINTS.GENERATE_REPORT, data);
    return response.data;
  },

  listReports: async (): Promise<ReportListResponse> => {
    const response = await api.get<ReportListResponse>(API_ENDPOINTS.LIST_REPORTS);
    return response.data;
  },

  downloadReport: (filename: string): string => {
    return `${API_ENDPOINTS.DOWNLOAD_REPORT(filename)}`;
  },
};
