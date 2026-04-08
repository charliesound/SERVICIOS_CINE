import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { workflowApi } from '@/api'
import { IntentAnalysis, WorkflowPlanRequest } from '@/types'
import { 
  Sparkles, 
  Loader2, 
  AlertCircle, 
  Image,
  Video,
  Mic,
  FlaskConical,
  Brain,
  Target,
  Lightbulb
} from 'lucide-react'
import clsx from 'clsx'

const taskTypeIcons: Record<string, typeof Image> = {
  still: Image,
  video: Video,
  dubbing: Mic,
  experimental: FlaskConical,
}

const taskTypeColors: Record<string, { bg: string; border: string; text: string }> = {
  still: { bg: 'bg-blue-500/10', border: 'border-blue-500/20', text: 'text-blue-400' },
  video: { bg: 'bg-purple-500/10', border: 'border-purple-500/20', text: 'text-purple-400' },
  dubbing: { bg: 'bg-green-500/10', border: 'border-green-500/20', text: 'text-green-400' },
  experimental: { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400' },
}

interface WorkflowPlannerPanelProps {
  intent: string
  onIntentChange: (intent: string) => void
  onAnalysisComplete: (analysis: IntentAnalysis) => void
  disabled?: boolean
}

export default function WorkflowPlannerPanel({
  intent,
  onIntentChange,
  onAnalysisComplete,
  disabled,
}: WorkflowPlannerPanelProps) {
  const [analysisResult, setAnalysisResult] = useState<IntentAnalysis | null>(null)

  const planMutation = useMutation({
    mutationFn: (request: WorkflowPlanRequest) => workflowApi.planWorkflow(request),
    onSuccess: (data) => {
      setAnalysisResult(data)
      onAnalysisComplete(data)
    },
  })

  const handlePlan = () => {
    if (!intent.trim()) return
    planMutation.mutate({ intent, context: {} })
  }

  const TaskIcon = taskTypeIcons[analysisResult?.task_type || 'still'] || Image
  const taskColors = taskTypeColors[analysisResult?.task_type || 'still'] || taskTypeColors.still

  return (
    <div className="space-y-5">
      {/* Intent Input */}
      <div>
        <label className="label flex items-center gap-2">
          <Brain className="w-4 h-4 text-amber-400" />
          Describe your vision
        </label>
        <textarea
          value={intent}
          onChange={(e) => onIntentChange(e.target.value)}
          placeholder="e.g., A cinematic shot of a robot at sunset, with warm orange lighting and dramatic shadows..."
          className="input min-h-[120px] resize-none text-base leading-relaxed"
          disabled={disabled || planMutation.isPending}
        />
      </div>

      {/* Analyze Button */}
      <button
        onClick={handlePlan}
        disabled={!intent.trim() || planMutation.isPending || disabled}
        className={clsx(
          'w-full py-3.5 rounded-xl font-medium transition-all flex items-center justify-center gap-2',
          !intent.trim() || planMutation.isPending || disabled
            ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
            : 'btn-primary'
        )}
      >
        {planMutation.isPending ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Analyzing...
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            Analyze & Plan
          </>
        )}
      </button>

      {/* Error State */}
      {planMutation.isError && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>Analysis failed. Please try again.</span>
        </div>
      )}

      {/* Analysis Result */}
      {analysisResult && (
        <div className="p-5 rounded-2xl bg-dark-200/50 border border-white/5 space-y-5">
          {/* Task Type & Confidence */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={clsx('w-12 h-12 rounded-xl flex items-center justify-center border', taskColors.bg, taskColors.border)}>
                <TaskIcon className={clsx('w-6 h-6', taskColors.text)} />
              </div>
              <div>
                <p className="font-semibold text-white capitalize">{analysisResult.task_type}</p>
                <p className="text-sm text-slate-500">
                  Backend: <span className={taskColors.text}>{analysisResult.backend}</span>
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className={clsx(
                'text-3xl font-bold',
                analysisResult.confidence >= 0.8 ? 'text-green-400' :
                analysisResult.confidence >= 0.5 ? 'text-amber-400' : 'text-red-400'
              )}>
                {Math.round(analysisResult.confidence * 100)}%
              </div>
              <p className="text-xs text-slate-500">confidence</p>
            </div>
          </div>

          {/* Detected Workflow */}
          {analysisResult.detected_workflow && (
            <div className="flex items-center gap-3 p-4 rounded-xl bg-amber-500/5 border border-amber-500/10">
              <Target className="w-5 h-5 text-amber-400" />
              <div>
                <span className="text-slate-400 text-sm">Workflow:</span>
                <span className="text-amber-400 font-medium ml-2">{analysisResult.detected_workflow}</span>
              </div>
            </div>
          )}

          {/* Missing Inputs Warning */}
          {analysisResult.missing_inputs && analysisResult.missing_inputs.length > 0 && (
            <div className="flex items-center gap-3 p-4 rounded-xl bg-yellow-500/5 border border-yellow-500/10">
              <AlertCircle className="w-5 h-5 text-yellow-400" />
              <div>
                <span className="text-yellow-400 font-medium">Missing inputs:</span>
                <span className="text-slate-400 ml-2">{analysisResult.missing_inputs.join(', ')}</span>
              </div>
            </div>
          )}

          {/* Reasoning */}
          <div className="pt-4 border-t border-white/5">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              <span className="text-sm font-medium text-slate-300">AI Analysis</span>
            </div>
            <p className="text-slate-300 leading-relaxed">{analysisResult.reasoning}</p>
          </div>

          {/* Suggested Parameters */}
          {Object.keys(analysisResult.suggested_params).length > 0 && (
            <div className="pt-4 border-t border-white/5">
              <p className="text-sm font-medium text-slate-300 mb-3">Suggested Parameters</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(analysisResult.suggested_params).map(([key, value]) => (
                  <span key={key} className="px-3 py-1.5 bg-white/5 rounded-lg text-sm text-slate-300">
                    <span className="text-slate-500">{key}:</span>{' '}
                    <span className="font-medium text-white">{String(value)}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}