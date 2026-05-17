import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Download,
  FileText,
  Settings,
  ChevronRight,
  AlertTriangle,
} from 'lucide-react'
import { breakdownApi } from '@/api'
import { projectsApi } from '@/api'
import { BreakdownExportFormat } from '@/types/breakdown'

export default function BreakdownPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [exporting, setExporting] = useState<BreakdownExportFormat | null>(null)

  const { data: project, isLoading: isProjectLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId!),
    enabled: !!projectId,
  })

  const {
    data: scenesData,
    isLoading: isScenesLoading,
    error: scenesError,
  } = useQuery({
    queryKey: ['breakdown-scenes', projectId],
    queryFn: () => breakdownApi.getBreakdownScenes(projectId!),
    enabled: !!projectId,
    retry: false,
  })

  const {
    data: deptsData,
    isLoading: isDeptsLoading,
    error: deptsError,
  } = useQuery({
    queryKey: ['breakdown-departments', projectId],
    queryFn: () => breakdownApi.getBreakdownDepartments(projectId!),
    enabled: !!projectId,
    retry: false,
  })

  const handleExport = async (format: BreakdownExportFormat) => {
    if (!projectId) return
    try {
      setExporting(format)
      const blob = await breakdownApi.exportBreakdown(projectId, format)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `breakdown-${projectId}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Export failed', err)
      alert('Error exportando el desglose. Por favor intente nuevamente.')
    } finally {
      setExporting(null)
    }
  }

  // Check if blocked by module enforcement
  const isBlocked =
    (scenesError as any)?.response?.status === 403 ||
    (deptsError as any)?.response?.status === 403

  if (isBlocked) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="bg-amber-50 border-l-4 border-amber-400 p-6 rounded-md mb-8 shadow-sm">
          <div className="flex items-start">
            <AlertTriangle className="h-6 w-6 text-amber-400 mt-0.5 mr-4 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-medium text-amber-800">Módulo no disponible</h3>
              <div className="mt-2 text-amber-700">
                <p>
                  No tienes acceso al módulo de CID Breakdown para este proyecto. Contacta con tu
                  administrador para habilitar esta funcionalidad.
                </p>
              </div>
              <div className="mt-4">
                <button
                  onClick={() => navigate(`/projects/${projectId}`)}
                  className="px-4 py-2 bg-amber-100 text-amber-800 rounded hover:bg-amber-200 transition-colors font-medium text-sm"
                >
                  Volver al Proyecto
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (isProjectLoading || isScenesLoading || isDeptsLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const scenes = scenesData?.scenes || []
  const departments = deptsData?.departments || []

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumbs */}
      <nav className="flex items-center text-sm font-medium text-gray-500 space-x-2">
        <Link to="/projects" className="hover:text-gray-900 transition-colors">
          Proyectos
        </Link>
        <ChevronRight className="h-4 w-4" />
        <Link to={`/projects/${projectId}`} className="hover:text-gray-900 transition-colors">
          {project?.name || 'Proyecto'}
        </Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-gray-900">CID Breakdown</span>
      </nav>

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">CID Breakdown</h1>
          <p className="text-gray-500 mt-1">Desglose técnico inteligente de guion</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => handleExport('json')}
            disabled={!!exporting}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 text-sm font-medium"
          >
            {exporting === 'json' ? (
              <div className="h-4 w-4 rounded-full border-2 border-gray-300 border-t-gray-600 animate-spin" />
            ) : (
              <Download className="h-4 w-4" />
            )}
            JSON
          </button>
          <button
            onClick={() => handleExport('csv')}
            disabled={!!exporting}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 text-sm font-medium"
          >
            {exporting === 'csv' ? (
              <div className="h-4 w-4 rounded-full border-2 border-gray-300 border-t-gray-600 animate-spin" />
            ) : (
              <Download className="h-4 w-4" />
            )}
            CSV
          </button>
          <button
            onClick={() => handleExport('md')}
            disabled={!!exporting}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 text-sm font-medium shadow-sm"
          >
            {exporting === 'md' ? (
              <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
            ) : (
              <FileText className="h-4 w-4" />
            )}
            Markdown
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Scenes */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary-500" />
                Escenas ({scenes.length})
              </h2>
            </div>
            {scenes.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No hay escenas desglosadas todavía. Es necesario ejecutar Script Analysis Pro
                previamente.
              </div>
            ) : (
              <div className="divide-y divide-gray-100 max-h-[800px] overflow-y-auto">
                {scenes.map((scene, idx) => (
                  <div key={idx} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold">
                          {scene.scene_number || idx + 1}
                        </span>
                        <h3 className="font-medium text-gray-900">
                          {scene.heading || 'Sin encabezado'}
                        </h3>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {scene.int_ext && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded font-medium">
                          {scene.int_ext}
                        </span>
                      )}
                      {scene.location && (
                        <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded font-medium">
                          {scene.location}
                        </span>
                      )}
                      {scene.time_of_day && (
                        <span className="px-2 py-1 bg-amber-50 text-amber-700 text-xs rounded font-medium">
                          {scene.time_of_day}
                        </span>
                      )}
                    </div>
                    {scene.characters && scene.characters.length > 0 && (
                      <div className="mt-3">
                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-1">
                          Personajes
                        </span>
                        <p className="text-sm text-gray-700">{scene.characters.join(', ')}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Departments */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                <Settings className="h-5 w-5 text-secondary-500" />
                Departamentos ({departments.length})
              </h2>
            </div>
            {departments.length === 0 ? (
              <div className="p-8 text-center text-gray-500">No hay datos de departamentos.</div>
            ) : (
              <div className="divide-y divide-gray-100 max-h-[800px] overflow-y-auto">
                {departments.map((dept, idx) => (
                  <div key={idx} className="p-4 hover:bg-gray-50 transition-colors">
                    <h3 className="font-semibold text-gray-900 capitalize mb-2">
                      {dept.department?.replace('_', ' ')}
                    </h3>
                    {dept.items && dept.items.length > 0 ? (
                      <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                        {dept.items.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-400 italic">Sin elementos detectados</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
