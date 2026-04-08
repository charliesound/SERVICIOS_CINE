type ProjectSettingsProjectVariantProps = {
  variant: "project";
  projectId: string;
  projectTitleDraft: string;
  onProjectTitleDraftChange: (nextTitle: string) => void;
  canRename: boolean;
  renamingProjectId: string | null;
  onRenameProject: () => void;
  onExportProject: () => void;
  exportingProjectId: string | null;
  onImportProject: () => void;
  importingStorage: boolean;
  onResetStorage: () => void;
  resettingStorage: boolean;
};

type ProjectSettingsEmptyVariantProps = {
  variant: "empty";
  onSeedDemo: () => void;
  seedLoading: boolean;
  onImportProject: () => void;
  importingStorage: boolean;
};

type ProjectSettingsActionGroupProps = ProjectSettingsProjectVariantProps | ProjectSettingsEmptyVariantProps;

export default function ProjectSettingsActionGroup(props: ProjectSettingsActionGroupProps) {
  // Common Button Styles
  const btnBase = "inline-flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium transition-all duration-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed";
  const btnPrimary = "bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md";
  const btnSecondary = "bg-white text-blue-700 border border-blue-200 hover:bg-blue-50";
  const btnDanger = "bg-white text-red-600 border border-red-100 hover:bg-red-50 hover:text-red-700";

  // Icons
  const Icons = {
    Seed: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>
    ),
    Import: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
    ),
    Export: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
    ),
    Rename: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
    ),
    Reset: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
    ),
  };

  if (props.variant === "empty") {
    const seedDisabled = props.seedLoading || props.importingStorage;
    const importDisabled = props.seedLoading || props.importingStorage;

    return (
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={props.onSeedDemo}
          disabled={seedDisabled}
          className={`${btnBase} ${btnPrimary}`}
        >
          {Icons.Seed}
          {props.seedLoading ? "Inicializando..." : "Inicializar datos demo"}
        </button>
        <button
          type="button"
          onClick={props.onImportProject}
          disabled={importDisabled}
          className={`${btnBase} ${btnSecondary}`}
        >
          {Icons.Import}
          {props.importingStorage ? "Importando..." : "Importar proyecto"}
        </button>
      </div>
    );
  }

  const renameDisabled = props.renamingProjectId !== null || props.resettingStorage;
  const anyGlobalLoading =
    props.exportingProjectId !== null ||
    props.importingStorage ||
    props.resettingStorage ||
    props.renamingProjectId !== null;

  return (
    <div className="flex flex-wrap items-center gap-3 mt-4 p-4 bg-gray-50/50 rounded-xl border border-gray-100">
      <div className="flex-1 min-w-[240px]">
        <input
          type="text"
          value={props.projectTitleDraft}
          onChange={(event) => props.onProjectTitleDraftChange(event.target.value)}
          placeholder="Nombre del proyecto..."
          disabled={renameDisabled}
          className="w-full px-4 py-2 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all disabled:bg-gray-50 disabled:text-gray-400"
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={props.onRenameProject}
          disabled={!props.canRename || renameDisabled}
          className={`${btnBase} ${btnSecondary}`}
          title="Renombrar proyecto"
        >
          {Icons.Rename}
          <span className="hidden sm:inline">
            {props.renamingProjectId === props.projectId ? "Guardando..." : "Renombrar"}
          </span>
        </button>

        <button
          type="button"
          onClick={props.onExportProject}
          disabled={anyGlobalLoading}
          className={`${btnBase} ${btnSecondary}`}
          title="Exportar proyecto como JSON"
        >
          {Icons.Export}
          <span className="hidden sm:inline">
            {props.exportingProjectId === props.projectId ? "Exportando..." : "Exportar"}
          </span>
        </button>

        <button
          type="button"
          onClick={props.onImportProject}
          disabled={anyGlobalLoading}
          className={`${btnBase} ${btnSecondary}`}
          title="Importar proyecto desde JSON"
        >
          {Icons.Import}
          <span className="hidden sm:inline">
            {props.importingStorage ? "Importando..." : "Importar"}
          </span>
        </button>

        <div className="h-6 w-px bg-gray-200 mx-1 hidden sm:block" />

        <button
          type="button"
          onClick={props.onResetStorage}
          disabled={anyGlobalLoading}
          className={`${btnBase} ${btnDanger}`}
          title="Resetear storage activo"
        >
          {Icons.Reset}
          <span className="hidden sm:inline">
            {props.resettingStorage ? "Reseteando..." : "Reset"}
          </span>
        </button>
      </div>
    </div>
  );
}
