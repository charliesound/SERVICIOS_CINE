import { useState } from 'react'
import { useWorkflowCatalog, usePresets } from '@/hooks'
import { useAuthStore } from '@/store'
import { Search, Image, Video, Mic, FlaskConical, Bookmark, GitBranch, Sparkles } from 'lucide-react'
import clsx from 'clsx'

const categoryIcons: Record<string, typeof Image> = {
  still: Image,
  video: Video,
  dubbing: Mic,
  lab: FlaskConical,
}

const categoryColors: Record<string, { bg: string; border: string; text: string }> = {
  still: { bg: 'bg-blue-500/10', border: 'border-blue-500/20', text: 'text-blue-400' },
  video: { bg: 'bg-purple-500/10', border: 'border-purple-500/20', text: 'text-purple-400' },
  dubbing: { bg: 'bg-green-500/10', border: 'border-green-500/20', text: 'text-green-400' },
  lab: { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400' },
}

export default function WorkflowsPage() {
  const { user } = useAuthStore()
  const { data: workflows, isLoading } = useWorkflowCatalog()
  const { data: presets } = usePresets({ user_id: user?.user_id })
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const filteredWorkflows = workflows?.filter(w => {
    const matchesSearch = w.name.toLowerCase().includes(search.toLowerCase()) ||
                          w.description.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = !selectedCategory || w.category === selectedCategory
    return matchesSearch && matchesCategory
  }) || []

  const categories = [...new Set(workflows?.map(w => w.category) || [])]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="heading-lg flex items-center gap-3">
            <GitBranch className="w-6 h-6 text-amber-400" />
            Workflows
          </h1>
          <p className="text-slate-400 mt-1">Explore AI generation pipelines</p>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search workflows..."
            className="input pl-12"
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={clsx(
              'px-4 py-2 rounded-xl text-sm font-medium transition-all',
              !selectedCategory
                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                : 'bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white'
            )}
          >
            All
          </button>
          {categories.map((cat) => {
            const Icon = categoryIcons[cat] || Image
            const colors = categoryColors[cat] || categoryColors.still
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={clsx(
                  'px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 capitalize',
                  selectedCategory === cat
                    ? `${colors.bg} ${colors.text} border ${colors.border}`
                    : 'bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white'
                )}
              >
                <Icon className="w-4 h-4" />
                {cat}
              </button>
            )
          })}
        </div>
      </div>

      {/* User Presets */}
      {presets && presets.length > 0 && (
        <div className="card card-hover">
          <div className="flex items-center gap-2 mb-4">
            <Bookmark className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-semibold text-white">My Presets</h2>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {presets.map((preset) => (
              <div key={preset.id} className="p-4 rounded-xl bg-dark-300/50 border border-white/5 hover:border-amber-500/20 transition-all cursor-pointer">
                <p className="font-medium text-white">{preset.name}</p>
                <p className="text-sm text-slate-500">{preset.workflow_key}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Workflows Grid */}
      {isLoading ? (
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 w-24 bg-slate-700 rounded mb-2" />
              <div className="h-3 w-full bg-slate-700 rounded" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {filteredWorkflows.map((workflow) => {
            const Icon = categoryIcons[workflow.category] || Image
            const colors = categoryColors[workflow.category] || categoryColors.still
            
            return (
              <div key={workflow.key} className="card card-hover cursor-pointer group">
                <div className="flex items-start justify-between mb-3">
                  <div className={clsx('p-2.5 rounded-xl border', colors.bg, colors.border)}>
                    <Icon className={clsx('w-5 h-5', colors.text)} />
                  </div>
                  <span className="text-xs text-slate-500 px-2 py-1 rounded bg-white/5">
                    {workflow.backend}
                  </span>
                </div>
                <h3 className="font-semibold text-white mb-2 group-hover:text-amber-400 transition-colors">{workflow.name}</h3>
                <p className="text-sm text-slate-400 mb-4 line-clamp-2">{workflow.description}</p>
                <div className="flex flex-wrap gap-2">
                  {workflow.tags.slice(0, 3).map((tag) => (
                    <span key={tag} className="px-2 py-1 bg-white/5 rounded-md text-xs text-slate-400">
                      {tag}
                    </span>
                  ))}
                  {workflow.tags.length > 3 && (
                    <span className="px-2 py-1 text-xs text-slate-500">+{workflow.tags.length - 3}</span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Empty state */}
      {filteredWorkflows.length === 0 && !isLoading && (
        <div className="card text-center py-16">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center mx-auto mb-4">
            <Sparkles className="w-8 h-8 text-amber-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">No workflows found</h3>
          <p className="text-slate-400">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  )
}