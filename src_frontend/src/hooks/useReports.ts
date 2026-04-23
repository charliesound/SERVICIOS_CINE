import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { reportsApi } from '@/api'
import { StructuredReportPayload, StructuredReportType } from '@/types'

const reportKeys = {
  list: (reportType: StructuredReportType) => ['reports', reportType] as const,
  detail: (reportType: StructuredReportType, reportId: string) => ['report', reportType, reportId] as const,
}

export function useReports(reportType: StructuredReportType) {
  return useQuery({
    queryKey: reportKeys.list(reportType),
    queryFn: () => reportsApi.listReports(reportType),
    enabled: !!reportType,
  })
}

export function useReport(reportType: StructuredReportType, reportId: string) {
  return useQuery({
    queryKey: reportKeys.detail(reportType, reportId),
    queryFn: () => reportsApi.getReport(reportType, reportId),
    enabled: !!reportType && !!reportId,
  })
}

export function useCreateReport(reportType: StructuredReportType) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: StructuredReportPayload) => reportsApi.createReport(reportType, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.list(reportType) })
    },
  })
}

export function useUpdateReport(reportType: StructuredReportType, reportId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: StructuredReportPayload) => reportsApi.updateReport(reportType, reportId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.list(reportType) })
      queryClient.invalidateQueries({ queryKey: reportKeys.detail(reportType, reportId) })
    },
  })
}
