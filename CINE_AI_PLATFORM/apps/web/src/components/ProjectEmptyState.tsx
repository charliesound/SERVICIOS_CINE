import ProjectSettingsActionGroup from "./ProjectSettingsActionGroup";

interface ProjectEmptyStateProps {
  onSeedDemo: () => void;
  seedLoading: boolean;
  onImportProject: () => void;
  importingStorage: boolean;
  seedError?: string;
}

export default function ProjectEmptyState({
  onSeedDemo,
  seedLoading,
  onImportProject,
  importingStorage,
  seedError,
}: ProjectEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <div className="bg-white border border-gray-100 rounded-2xl p-8 shadow-sm max-w-md w-full">
        <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Panel sin datos demo</h2>
        <p className="text-gray-500 mb-8">Para una experiencia completa, ejecuta <code className="rounded bg-gray-100 px-1.5 py-0.5 text-sm text-gray-700">node scripts/seed-demo.js</code> en tu terminal.</p>
        
        <div className="flex flex-col gap-3">
          <ProjectSettingsActionGroup
            variant="empty"
            onSeedDemo={onSeedDemo}
            seedLoading={seedLoading}
            onImportProject={onImportProject}
            importingStorage={importingStorage}
          />
        </div>
        
        {seedError ? (
          <div className="mt-4 p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-100">
            {seedError}
          </div>
        ) : null}
      </div>
    </div>
  );
}
