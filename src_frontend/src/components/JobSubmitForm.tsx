import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { renderApi } from '@/api'
import { useJobStore, useAuthStore } from '@/store'
import { IntentAnalysis, JobCreate, TaskType } from '@/types'
import { 
  Loader2, 
  AlertCircle, 
  Image,
  Video,
  Mic,
  FlaskConical,
  Play,
  Sparkles
} from 'lucide-react'
import clsx from 'clsx'

const taskTypes: { type: TaskType; icon: typeof Image; label: string; description: string; color: string }[] = [
  { type: 'still', icon: Image, label: 'Image', description: 'AI image generation', color: 'blue' },
  { type: 'video', icon: Video, label: 'Video', description: 'Video generation', color: 'purple' },
  { type: 'dubbing', icon: Mic, label: 'Audio', description: 'Voice & dubbing', color: 'green' },
  { type: 'experimental', icon: FlaskConical, label: 'Lab', description: 'Experimental features', color: 'amber' },
]

const colorMap: Record<string, { bg: string; border: string; text: string; hover: string }> = {
  blue: { bg: 'bg-blue-500/10', border: 'border-blue-500/20', text: 'text-blue-400', hover: 'hover:border-blue-500/40' },
  purple: { bg: 'bg-purple-500/10', border: 'border-purple-500/20', text: 'text-purple-400', hover: 'hover:border-purple-500/40' },
  green: { bg: 'bg-green-500/10', border: 'border-green-500/20', text: 'text-green-400', hover: 'hover:border-green-500/40' },
  amber: { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400', hover: 'hover:border-amber-500/40' },
}

interface JobSubmitFormProps {
  analysis: IntentAnalysis | null
  onJobCreated: (jobId: string) => void
  planTaskTypes: string[]
}

export default function JobSubmitForm({ analysis, onJobCreated, planTaskTypes }: JobSubmitFormProps) {
  const { user } = useAuthStore()
  const { setIsSubmitting, isSubmitting } = useJobStore()
  const [selectedTaskType, setSelectedTaskType] = useState<TaskType | null>(analysis?.task_type as TaskType || null)
  const [prompt, setPrompt] = useState('')

  const createJobMutation = useMutation({
    mutationFn: (job: JobCreate) => renderApi.createJob(job),
    onMutate: () => setIsSubmitting(true),
    onSuccess: (data) => {
      if (data.status !== 'failed') {
        onJobCreated(data.job_id)
      }
    },
    onSettled: () => setIsSubmitting(false),
  })

  const handleSubmit = () => {
    if (!selectedTaskType || !prompt.trim() || !user) return

    const job: JobCreate = {
      task_type: selectedTaskType,
      workflow_key: analysis?.detected_workflow || `${selectedTaskType}_text_to_${selectedTaskType}_base`,
      prompt: {
        positive: prompt,
        negative: 'blurry, low quality, distorted',
      },
      user_id: user.user_id,
      user_plan: user.plan,
      priority: 5,
    }

    createJobMutation.mutate(job)
  }

  const isAllowed = (type: TaskType) => planTaskTypes.includes(type) || planTaskTypes.includes('all')

  return (
    <div className="space-y-5">
      {/* Task Type Selection */}
      <div>
        <label className="label flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-400" />
          Select Type
        </label>
        <div className="grid grid-cols-2 gap-3">
          {taskTypes.map(({ type, icon: Icon, label, description, color }) => {
            const allowed = isAllowed(type)
            const selected = selectedTaskType === type
            const colors = colorMap[color]
            
            return (
              <button
                key={type}
                onClick={() => allowed && setSelectedTaskType(type)}
                disabled={!allowed}
                className={clsx(
                  'p-4 rounded-xl border transition-all text-left group',
                  selected
                    ? `${colors.bg} ${colors.border} ring-2 ring-amber-500/30`
                    : allowed
                      ? 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
                      : 'bg-white/5 border-white/5 opacity-40 cursor-not-allowed'
                )}
              >
                <div className="flex items-center gap-3">
                  <div className={clsx(
                    'w-9 h-9 rounded-lg flex items-center justify-center',
                    selected ? colors.bg : 'bg-white/5'
                  )}>
                    <Icon className={clsx('w-4 h-4', selected ? colors.text : 'text-slate-400')} />
                  </div>
                  <div>
                    <span className={clsx('font-medium', selected ? 'text-white' : 'text-slate-300')}>
                      {label}
                    </span>
                  </div>
                </div>
                <p className={clsx('text-xs mt-2', selected ? colors.text : 'text-slate-500')}>
                  {allowed ? description : 'Not in your plan'}
                </p>
              </button>
            )
          })}
        </div>
      </div>

      {/* Prompt Input */}
      <div>
        <label className="label">Prompt</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your vision in detail..."
          className="input min-h-[140px] resize-none text-base"
          disabled={isSubmitting}
        />
        <p className="text-xs text-slate-500 mt-2">
          Be specific about subject, style, lighting, composition, and mood
        </p>
      </div>

      {/* Detected Workflow */}
      {analysis && (
        <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/10">
          <div className="flex items-center gap-2 text-sm">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span className="text-slate-400">Workflow:</span>
            <span className="text-amber-400 font-medium">{analysis.detected_workflow}</span>
          </div>
        </div>
      )}

      {/* Error Message */}
      {createJobMutation.data?.status === 'failed' && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{createJobMutation.data.error || 'Failed to create job'}</span>
        </div>
      )}

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={!selectedTaskType || !prompt.trim() || isSubmitting}
        className={clsx(
          'w-full py-3.5 rounded-xl font-medium transition-all flex items-center justify-center gap-2',
          !selectedTaskType || !prompt.trim() || isSubmitting
            ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
            : 'btn-primary'
        )}
      >
        {isSubmitting ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Creating Project...
          </>
        ) : (
          <>
            <Play className="w-5 h-5" />
            Launch Project
          </>
        )}
      </button>
    </div>
  )
}