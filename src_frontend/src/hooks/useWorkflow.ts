import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { workflowApi } from '@/api'
import { WorkflowPlanRequest, PresetCreate } from '@/types'

export function useWorkflowCatalog() {
  return useQuery({
    queryKey: ['workflowCatalog'],
    queryFn: workflowApi.getCatalog,
  })
}

export function usePlanWorkflow() {
  return useMutation({
    mutationFn: (request: WorkflowPlanRequest) => workflowApi.planWorkflow(request),
  })
}

export function useBuildWorkflow() {
  return useMutation({
    mutationFn: ({ workflowKey, inputs }: { workflowKey: string; inputs: Record<string, any> }) =>
      workflowApi.buildWorkflow(workflowKey, inputs),
  })
}

export function usePresets(params?: { user_id?: string; category?: string }) {
  return useQuery({
    queryKey: ['presets', params],
    queryFn: () => workflowApi.getPresets(params),
  })
}

export function useCreatePreset() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ preset, userId }: { preset: PresetCreate; userId: string }) =>
      workflowApi.createPreset(preset, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['presets'] })
    },
  })
}
