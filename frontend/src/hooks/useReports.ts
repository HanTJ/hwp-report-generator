import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reportApi } from '../services/reportApi';
import type { ReportRequest } from '../types/report';

export const useReports = () => {
  const queryClient = useQueryClient();

  const { data: reportsData, isLoading, refetch } = useQuery({
    queryKey: ['reports'],
    queryFn: reportApi.listReports,
  });

  const generateMutation = useMutation({
    mutationFn: (data: ReportRequest) => reportApi.generateReport(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
  });

  return {
    reports: reportsData?.reports || [],
    isLoading,
    refetch,
    generateReport: generateMutation.mutateAsync,
    isGenerating: generateMutation.isPending,
  };
};
