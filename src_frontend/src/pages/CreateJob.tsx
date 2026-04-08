import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore, useJobStore } from '@/store'
import { useUserPlanStatus } from '@/hooks'
import WorkflowPlannerPanel from '@/components/WorkflowPlannerPanel'
import JobSubmitForm from '@/components/JobSubmitForm'
import { IntentAnalysis } from '@/types'
import { ArrowLeft, CheckCircle, Sparkles } from 'lucide-react'

export default function CreateJob() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { intent, setIntent, analysis, setAnalysis } = useJobStore()
  const { data: planStatus } = useUserPlanStatus(user?.user_id || '', user?.plan || 'free')
  
  const [createdJobId, setCreatedJobId] = useState<string | null>(null)

  const handleAnalysisComplete = (result: IntentAnalysis) => {
    setAnalysis(result)
  }

  const handleJobCreated = (jobId: string) => {
    setCreatedJobId(jobId)
  }

  const planTaskTypes = planStatus?.plan 
    ? (planStatus as any)?.limits?.allowed_task_types || ['still']
    : ['still']

  if (createdJobId) {
    return (
      <div className="max-w-md mx-auto text-center py-12">
        <div className="card bg-dark-200/80 backdrop-blur-xl">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-green-500/20 to-green-600/10 flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-3">Project Created!</h2>
          <p className="text-slate-400 mb-6">
            Your job <span className="font-mono text-amber-400">{createdJobId}</span> has been queued for processing.
          </p>
          <div className="flex flex-col gap-3">
            <button
              onClick={() => navigate('/queue')}
              className="btn-primary w-full"
            >
              View in Queue
            </button>
            <button
              onClick={() => {
                setCreatedJobId(null)
                useJobStore.getState().reset()
              }}
              className="btn-secondary w-full"
            >
              Create Another
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={() => navigate('/')}
          className="p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-slate-400" />
        </button>
        <div>
          <h1 className="heading-lg flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-amber-400" />
            Create New Project
          </h1>
          <p className="text-slate-400 mt-1">Describe your vision and let AI bring it to life</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Left - Workflow Planner */}
        <div className="card card-hover">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-amber-400" />
            </div>
            <h2 className="text-lg font-semibold text-white">Describe Your Vision</h2>
          </div>
          <WorkflowPlannerPanel
            intent={intent}
            onIntentChange={setIntent}
            onAnalysisComplete={handleAnalysisComplete}
            disabled={!planStatus?.can_submit_active && !planStatus?.can_submit_queued}
          />
        </div>

        {/* Right - Submit & Plan Info */}
        <div className="space-y-4">
          <div className="card card-hover">
            <h2 className="text-lg font-semibold text-white mb-4">Project Details</h2>
            <JobSubmitForm
              analysis={analysis}
              onJobCreated={handleJobCreated}
              planTaskTypes={planTaskTypes}
            />
          </div>

          {planStatus && (
            <div className="card bg-dark-200/50">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-slate-300">Your Plan</h3>
                <span className={`badge ${
                  user?.plan === 'studio' ? 'badge-studio' :
                  user?.plan === 'enterprise' ? 'badge-enterprise' :
                  'badge-free'
                }`}>
                  {user?.plan}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-xl bg-dark-300/50">
                  <p className="text-2xl font-bold text-white">
                    {planStatus.active_jobs}
                    <span className="text-sm text-slate-500 font-normal">
                      /{planStatus.max_active_jobs === -1 ? '∞' : planStatus.max_active_jobs}
                    </span>
                  </p>
                  <p className="text-xs text-slate-400">Active Jobs</p>
                </div>
                <div className="p-3 rounded-xl bg-dark-300/50">
                  <p className="text-2xl font-bold text-white">
                    {planStatus.queued_jobs}
                    <span className="text-sm text-slate-500 font-normal">
                      /{planStatus.max_queued_jobs === -1 ? '∞' : planStatus.max_queued_jobs}
                    </span>
                  </p>
                  <p className="text-xs text-slate-400">Queued</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-white/5">
                <p className="text-xs text-slate-500">
                  Allowed: <span className="text-slate-400">{planTaskTypes.join(', ')}</span>
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}