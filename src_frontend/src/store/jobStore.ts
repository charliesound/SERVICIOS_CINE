import { create } from 'zustand'
import { TaskType, IntentAnalysis, JobResponse } from '@/types'

interface JobState {
  taskType: TaskType | null
  intent: string
  analysis: IntentAnalysis | null
  createdJob: JobResponse | null
  isPlanning: boolean
  isSubmitting: boolean
  setTaskType: (type: TaskType | null) => void
  setIntent: (intent: string) => void
  setAnalysis: (analysis: IntentAnalysis | null) => void
  setCreatedJob: (job: JobResponse | null) => void
  setIsPlanning: (planning: boolean) => void
  setIsSubmitting: (submitting: boolean) => void
  reset: () => void
}

export const useJobStore = create<JobState>((set) => ({
  taskType: null,
  intent: '',
  analysis: null,
  createdJob: null,
  isPlanning: false,
  isSubmitting: false,
  setTaskType: (taskType) => set({ taskType }),
  setIntent: (intent) => set({ intent }),
  setAnalysis: (analysis) => set({ analysis }),
  setCreatedJob: (createdJob) => set({ createdJob }),
  setIsPlanning: (isPlanning) => set({ isPlanning }),
  setIsSubmitting: (isSubmitting) => set({ isSubmitting }),
  reset: () => set({
    taskType: null,
    intent: '',
    analysis: null,
    createdJob: null,
    isPlanning: false,
    isSubmitting: false,
  }),
}))
