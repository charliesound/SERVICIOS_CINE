import { useState } from "react";
import ProjectSettingsActionGroup from "./ProjectSettingsActionGroup";
import type { Project } from "../types/project";
import type { Character } from "../types/character";
import type { Scene } from "../types/scene";
import type { Shot } from "../types/shot";

type ProjectCardProps = {
  project: Project;
  characters: Character[];
  scenes: Scene[];
  shots: Shot[];
  selectedShotId: string | null;
  onSelectShot: (shot: Shot | null) => void;
  onRenameProject: (project: Project, newTitle: string) => Promise<void>;
  onExportProject: (project: Project) => void;
  onImportProject: () => void;
  onResetStorage: () => void;
  onAddCharacterToProject: (project: Project, name: string) => Promise<void>;
  onDeleteCharacter: (characterId: string) => Promise<void>;
  onUpdateCharacter: (characterId: string, name: string, seed: number, references: string[]) => Promise<void>;
  onAddSceneToProject: (projectId: string) => Promise<void>;
  onDeleteScene: (sceneId: string) => Promise<void>;
  onAddShotToScene: (sceneId: string) => Promise<void>;
  onDeleteShot: (shotId: string) => Promise<void>;
  exportingProjectId: string | null;
  importingStorage: boolean;
  renamingProjectId: string | null;
  resettingStorage: boolean;
  creatingCharacterProjectId: string | null;
  deletingCharacterId: string | null;
  updatingCharacterId: string | null;
  creatingSceneProjectId: string | null;
  deletingSceneId: string | null;
  creatingShotSceneId: string | null;
  deletingShot: boolean;
};

export default function ProjectCard({
  project,
  characters,
  scenes,
  shots,
  onRenameProject,
  onExportProject,
  onImportProject,
  onResetStorage,
  onAddCharacterToProject,
  onDeleteCharacter,
  onUpdateCharacter,
  onAddSceneToProject,
  onDeleteScene,
  onAddShotToScene,
  exportingProjectId,
  importingStorage,
  renamingProjectId,
  resettingStorage,
  creatingCharacterProjectId,
  deletingCharacterId,
  updatingCharacterId,
  creatingSceneProjectId,
  deletingSceneId,
  creatingShotSceneId,
}: ProjectCardProps) {
  const [projectTitleDraft, setProjectTitleDraft] = useState(project.title);
  const [characterNameDraft, setCharacterNameDraft] = useState("");
  const [editingCharacterId, setEditingCharacterId] = useState<string | null>(null);
  const [editingCharacterNameDraft, setEditingCharacterNameDraft] = useState("");
  const [editingCharacterSeedDraft, setEditingCharacterSeedDraft] = useState("");
  const [editingCharacterReferencesDraft, setEditingCharacterReferencesDraft] = useState<string[]>([]);
  const [editingCharacterReferenceDraft, setEditingCharacterReferenceDraft] = useState("");
  const [editingCharacterSaveError, setEditingCharacterSaveError] = useState("");

  const handleRenameClick = () => {
    const trimmedTitle = projectTitleDraft.trim();
    if (trimmedTitle !== "" && trimmedTitle !== project.title) {
      onRenameProject(project, trimmedTitle);
    }
  };

  const handleAddCharacterClick = async () => {
    const trimmedName = characterNameDraft.trim();
    if (trimmedName !== "") {
      try {
        await onAddCharacterToProject(project, trimmedName);
        setCharacterNameDraft("");
      } catch {
        // Error handled by parent
      }
    }
  };

  const handleEditCharacterClick = (character: Character) => {
    setEditingCharacterId(character.id);
    setEditingCharacterNameDraft(character.name);
    setEditingCharacterSeedDraft(character.seed_master.toString());
    setEditingCharacterReferencesDraft([...character.reference_images]);
    setEditingCharacterReferenceDraft("");
    setEditingCharacterSaveError("");
  };

  const handleCancelEditCharacterClick = () => {
    setEditingCharacterId(null);
    setEditingCharacterNameDraft("");
    setEditingCharacterSeedDraft("");
    setEditingCharacterReferencesDraft([]);
    setEditingCharacterReferenceDraft("");
    setEditingCharacterSaveError("");
  };

  const handleAddReferenceImage = () => {
    const trimmed = editingCharacterReferenceDraft.trim();
    if (trimmed !== "") {
      if (!editingCharacterReferencesDraft.includes(trimmed)) {
        setEditingCharacterReferencesDraft([...editingCharacterReferencesDraft, trimmed]);
      }
      setEditingCharacterReferenceDraft("");
      setEditingCharacterSaveError("");
    }
  };

  const handleRemoveReferenceImage = (index: number) => {
    setEditingCharacterReferencesDraft(editingCharacterReferencesDraft.filter((_, i) => i !== index));
    setEditingCharacterSaveError("");
  };

  const handleSaveCharacterClick = async (characterId: string) => {
    const trimmedName = editingCharacterNameDraft.trim();
    const seedDraft = editingCharacterSeedDraft.trim();
    const parsedSeed = seedDraft === "" ? 0 : Number(seedDraft);
    const normalizedReferences = editingCharacterReferencesDraft
      .map((item) => item.trim())
      .filter((item) => item.length > 0);

    if (trimmedName === "") {
      setEditingCharacterSaveError("El nombre no puede estar vacío.");
      return;
    }

    if (!Number.isFinite(parsedSeed) || !Number.isInteger(parsedSeed)) {
      setEditingCharacterSaveError("El seed_master debe ser un número entero.");
      return;
    }

    setEditingCharacterSaveError("");

    try {
      await onUpdateCharacter(characterId, trimmedName, Math.trunc(parsedSeed), normalizedReferences);
      setEditingCharacterId(null);
    } catch {
      setEditingCharacterSaveError("No se pudo guardar el personaje.");
    }
  };

  const areSameReferenceImages = (a: string[], b: string[]) => {
    if (a.length !== b.length) return false;
    const sortedA = [...a].sort();
    const sortedB = [...b].sort();
    return sortedA.every((val, index) => val === sortedB[index]);
  };

  const canRename = projectTitleDraft.trim() !== "" && projectTitleDraft.trim() !== project.title;
  const canAddCharacter = characterNameDraft.trim() !== "";

  // UI Components
  const btnBase = "inline-flex items-center justify-center gap-2 px-3 py-1.5 text-xs font-medium transition-all duration-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed";
  const btnPrimary = "bg-blue-600 text-white hover:bg-blue-700 shadow-sm";
  const btnSecondary = "bg-white text-gray-700 border border-gray-200 hover:bg-gray-50 hover:border-blue-200";
  const btnDanger = "bg-white text-red-600 border border-red-100 hover:bg-red-50 hover:text-red-700";

  return (
    <div className="bg-white border border-gray-100 rounded-2xl p-6 mb-6 shadow-sm hover:shadow-md transition-all">
      <div className="flex flex-col gap-1 mb-2">
        <h3 className="text-xl font-bold text-gray-900 tracking-tight m-0">{project.title}</h3>
        {project.description && <p className="text-gray-500 text-sm mt-1">{project.description}</p>}
        <code className="text-[10px] text-gray-400 font-mono tracking-widest uppercase mt-1">ID: {project.id}</code>
      </div>

      <div className="flex gap-4 mb-4">
        <div className="flex items-center gap-1.5 text-[11px] text-gray-500 bg-gray-50 px-2 py-1 rounded-lg border border-gray-100">
          <span className="font-bold text-gray-700">{scenes.length}</span> Escenas
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-gray-500 bg-gray-50 px-2 py-1 rounded-lg border border-gray-100">
          <span className="font-bold text-gray-700">{shots.length}</span> Planos
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-gray-500 bg-gray-50 px-2 py-1 rounded-lg border border-gray-100">
          <span className="font-bold text-gray-700">{characters.length}</span> Personajes
        </div>
      </div>

      <ProjectSettingsActionGroup
        variant="project"
        projectId={project.id}
        projectTitleDraft={projectTitleDraft}
        onProjectTitleDraftChange={setProjectTitleDraft}
        canRename={canRename}
        renamingProjectId={renamingProjectId}
        onRenameProject={handleRenameClick}
        onExportProject={() => onExportProject(project)}
        exportingProjectId={exportingProjectId}
        onImportProject={onImportProject}
        importingStorage={importingStorage}
        onResetStorage={onResetStorage}
        resettingStorage={resettingStorage}
      />

      <div className="mt-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 bg-gray-50/50 rounded-xl border border-gray-100 mb-6">
          <div className="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" x2="19" y1="8" y2="14"/><line x1="22" x2="16" y1="11" y2="11"/></svg>
            <strong className="text-gray-700 text-sm">Personajes</strong>
          </div>
          <div className="flex gap-2 w-full sm:w-auto">
            <input
              type="text"
              value={characterNameDraft}
              onChange={(e) => setCharacterNameDraft(e.target.value)}
              disabled={creatingCharacterProjectId !== null || deletingCharacterId !== null || updatingCharacterId !== null}
              placeholder="Nombre del nuevo personaje..."
              className="flex-1 sm:w-64 px-4 py-2 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all disabled:opacity-50"
            />
            <button
              type="button"
              onClick={handleAddCharacterClick}
              disabled={!canAddCharacter || creatingCharacterProjectId !== null || deletingCharacterId !== null || updatingCharacterId !== null}
              className={`${btnBase} ${btnPrimary} px-4 py-2 text-sm`}
            >
              {creatingCharacterProjectId === project.id ? "Añadiendo..." : "Añadir"}
            </button>
          </div>
        </div>

        {/* Nueva sección de Acciones Rápidas de Estructura */}
        <div className="flex gap-3 mb-6">
          <button
            type="button"
            onClick={() => onAddSceneToProject(project.id)}
            disabled={creatingSceneProjectId !== null}
            className={`${btnBase} ${btnSecondary} flex-1 py-3 text-sm font-bold border-dashed border-2 hover:border-blue-300 hover:text-blue-700`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3h18v18H3z"/><path d="M9 3v18"/><path d="M3 9h18"/></svg>
            {creatingSceneProjectId === project.id ? "Creando Escena..." : "Nueva Escena"}
          </button>
        </div>

        {characters.length === 0 ? (
          <div className="text-center py-12 bg-gray-50/30 rounded-2xl border border-dashed border-gray-200">
            <p className="text-gray-400 text-sm">No hay personajes definidos para este proyecto.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {characters.map((character: Character) => {
              const isEditingCharacter = editingCharacterId === character.id;
              const normalizedEditingNameDraft = editingCharacterNameDraft.trim();
              const parsedSeedDraft = Number(editingCharacterSeedDraft);
              const hasEmptyCharacterName = isEditingCharacter && normalizedEditingNameDraft === "";
              const hasInvalidCharacterSeed = isEditingCharacter && !Number.isInteger(parsedSeedDraft);
              
              const normalizedEditingReferenceImages = editingCharacterReferencesDraft
                .map((item) => item.trim())
                .filter((item) => item.length > 0);
              const normalizedCharacterReferenceImages = character.reference_images
                .map((item) => item.trim())
                .filter((item) => item.length > 0);
              const hasReferenceImagesChanged =
                isEditingCharacter &&
                !areSameReferenceImages(normalizedEditingReferenceImages, normalizedCharacterReferenceImages);

              const canSaveCharacter =
                isEditingCharacter &&
                !hasEmptyCharacterName &&
                !hasInvalidCharacterSeed &&
                (
                  normalizedEditingNameDraft !== character.name ||
                  parsedSeedDraft !== character.seed_master ||
                  hasReferenceImagesChanged
                );

              return (
                <div key={character.id} className="group bg-white border border-gray-100 rounded-xl p-5 hover:border-blue-200 hover:shadow-sm transition-all">
                  {isEditingCharacter ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-3">
                        <div className="space-y-1">
                          <label className="text-[10px] text-gray-400 uppercase font-bold px-1">Nombre</label>
                          <input
                            type="text"
                            title="Nombre del personaje"
                            value={editingCharacterNameDraft}
                            onChange={(e) => {
                              setEditingCharacterNameDraft(e.target.value);
                              setEditingCharacterSaveError("");
                            }}
                            disabled={updatingCharacterId !== null || deletingCharacterId !== null}
                            className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 outline-none"
                          />
                        </div>
                        <div className="space-y-1">
                          <label className="text-[10px] text-gray-400 uppercase font-bold px-1">Seed Master</label>
                          <input
                            type="number"
                            title="Semilla maestra"
                            value={editingCharacterSeedDraft}
                            onChange={(e) => {
                              setEditingCharacterSeedDraft(e.target.value);
                              setEditingCharacterSaveError("");
                            }}
                            disabled={updatingCharacterId !== null || deletingCharacterId !== null}
                            className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 outline-none"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <label className="text-[10px] text-gray-400 uppercase font-bold px-1">Imágenes de Referencia</label>
                        <div className="flex flex-wrap gap-2 mb-2">
                          {editingCharacterReferencesDraft.map((ref: string, idx: number) => (
                            <span key={idx} className="inline-flex items-center gap-1.5 px-2 py-1 bg-blue-50 text-blue-700 text-[11px] rounded-md border border-blue-100">
                              {ref.substring(0, 20)}...
                              <button
                                onClick={() => handleRemoveReferenceImage(idx)}
                                disabled={updatingCharacterId !== null || deletingCharacterId !== null}
                                className="hover:text-red-600 disabled:opacity-50"
                              >
                                ×
                              </button>
                            </span>
                          ))}
                        </div>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            placeholder="URL de referencia..."
                            value={editingCharacterReferenceDraft}
                            onChange={(e) => {
                              setEditingCharacterReferenceDraft(e.target.value);
                              setEditingCharacterSaveError("");
                            }}
                            disabled={updatingCharacterId !== null || deletingCharacterId !== null}
                            className="flex-1 px-3 py-1.5 text-xs border border-gray-200 rounded-lg outline-none"
                          />
                          <button
                            onClick={handleAddReferenceImage}
                            disabled={editingCharacterReferenceDraft.trim() === "" || updatingCharacterId !== null || deletingCharacterId !== null}
                            className={`${btnBase} ${btnSecondary}`}
                          >
                            +
                          </button>
                        </div>
                      </div>

                      <div className="flex justify-end gap-2 pt-2 border-t border-gray-50">
                        <button
                          onClick={handleCancelEditCharacterClick}
                          disabled={updatingCharacterId !== null}
                          className={`${btnBase} ${btnSecondary}`}
                        >
                          Cancelar
                        </button>
                        <button 
                          onClick={() => {
                            void handleSaveCharacterClick(character.id);
                          }}
                          disabled={!canSaveCharacter || updatingCharacterId !== null || deletingCharacterId !== null}
                          className={`${btnBase} ${btnPrimary}`}
                        >
                          {updatingCharacterId === character.id ? "Guardando..." : "Guardar"}
                        </button>
                      </div>

                      {hasEmptyCharacterName ? (
                        <p className="text-xs text-red-600">El nombre no puede estar vacío.</p>
                      ) : null}
                      {hasInvalidCharacterSeed ? (
                        <p className="text-xs text-red-600">El seed_master debe ser un número entero.</p>
                      ) : null}
                      {editingCharacterSaveError ? (
                        <p className="text-xs text-red-600">{editingCharacterSaveError}</p>
                      ) : null}
                    </div>
                  ) : (
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <h4 className="font-bold text-gray-900">{character.name}</h4>
                        <div className="flex items-center gap-3">
                          <span className="text-[11px] text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded border border-gray-100">
                            Seed: {character.seed_master}
                          </span>
                          <span className="text-[11px] text-gray-400">
                            {character.reference_images.length} refs
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => handleEditCharacterClick(character)} 
                          disabled={updatingCharacterId !== null || deletingCharacterId !== null || creatingCharacterProjectId !== null}
                          className={`${btnBase} ${btnSecondary} p-1.5`}
                          title="Editar Personaje"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
                        </button>
                        <button 
                          onClick={() => {
                            void onDeleteCharacter(character.id);
                          }}
                          disabled={deletingCharacterId !== null || creatingCharacterProjectId !== null || updatingCharacterId !== null}
                          className={`${btnBase} ${btnDanger} p-1.5`}
                          title="Eliminar Personaje"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Sección de Escenas */}
        <div className="mt-8 pt-8 border-t border-gray-100">
          <div className="flex items-center gap-2 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M8 7h6"/><path d="M8 11h8"/><path d="M8 15h6"/></svg>
            <strong className="text-gray-700 text-sm">Escenas</strong>
          </div>

          {scenes.length === 0 ? (
            <div className="text-center py-8 bg-gray-50/30 rounded-2xl border border-dashed border-gray-200">
              <p className="text-gray-400 text-sm">No hay escenas creadas.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {scenes.map((scene, idx) => (
                <div key={scene.id} className="group flex items-center justify-between p-3 bg-white border border-gray-100 rounded-xl hover:border-blue-200 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-xs">
                      {idx + 1}
                    </div>
                    <div>
                      <div className="text-sm font-bold text-gray-900">{scene.title || `Escena ${idx + 1}`}</div>
                      <div className="text-[10px] text-gray-400 uppercase font-bold tracking-tight">
                        {shots.filter(s => s.scene_id === scene.id).length} Planos
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => onAddShotToScene(scene.id)}
                      disabled={creatingShotSceneId === scene.id}
                      className={`${btnBase} ${btnSecondary} p-1.5`}
                      title="Añadir Plano"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                    </button>
                    <button
                      onClick={() => onDeleteScene(scene.id)}
                      disabled={deletingSceneId === scene.id}
                      className={`${btnBase} ${btnDanger} p-1.5`}
                      title="Eliminar Escena"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
