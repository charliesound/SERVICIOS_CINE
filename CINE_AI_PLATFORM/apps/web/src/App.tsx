import { useEffect, useRef, useState, type ChangeEvent } from "react";
import {
  createStorageCharacter,
  createStorageScene,
  createStorageShot,
  deleteStorageCharacter,
  deleteStorageScene,
  deleteStorageShot,
  exportStorageData,
  importStorageData,
  loadDashboardData,
  normalizeStorageImportPayload,
  renameStorageProject,
  resetStorageData,
  type StorageImportPayload,
  updateStorageCharacter,
  updateStorageShot,
  seedStorageData,
} from "./services/dashboardApi";
import ProjectCard from "./components/ProjectCard";
import ProjectEmptyState from "./components/ProjectEmptyState";
import LoginScreen from "./components/LoginScreen";
import ImportConfirmationModal, { type ImportPreviewData } from "./components/ImportConfirmationModal";
import SemanticContextPanel from "./components/SemanticContextPanel";
import ShotSemanticContextSummary from "./components/ShotSemanticContextSummary";
import SequenceExecutionPanel from "./components/SequenceExecutionPanel";
import ShotBuilderPanel from "./components/ShotBuilderPanel";
import { useAuthStore } from "./store/authStore";

import type { Project } from "./types/project";
import type { Character } from "./types/character";
import type { Scene } from "./types/scene";
import type { Shot } from "./types/shot";

type DashboardLoadState = "loading" | "error" | "empty" | "success";

type ImportPreview = ImportPreviewData & {
  payload: StorageImportPayload;
};


function getImportProjectLabel(project: Record<string, unknown> | null): string {
  if (!project) {
    return "Sin proyecto";
  }

  const title = typeof project.title === "string" ? project.title.trim() : "";
  if (title) {
    return title;
  }

  const name = typeof project.name === "string" ? project.name.trim() : "";
  if (name) {
    return name;
  }

  const id = typeof project.id === "string" ? project.id.trim() : "";
  if (id) {
    return id;
  }

  return "Proyecto sin nombre";
}

function getBackendErrorMessage(error: unknown): string | null {
  if (!error || typeof error !== "object") {
    return null;
  }

  const maybeResponse = (error as { response?: { data?: { error?: { message?: unknown } } } }).response;
  const message = maybeResponse?.data?.error?.message;

  if (typeof message !== "string") {
    return null;
  }

  const normalizedMessage = message.trim();
  return normalizedMessage === "" ? null : normalizedMessage;
}

function App() {
  const user = useAuthStore((state) => state.user);
  const sessionReady = useAuthStore((state) => state.sessionReady);
  const sessionLoading = useAuthStore((state) => state.sessionLoading);
  const loginError = useAuthStore((state) => state.loginError);
  const hydrateSession = useAuthStore((state) => state.hydrateSession);
  const login = useAuthStore((state) => state.login);
  const logout = useAuthStore((state) => state.logout);

  const [projects, setProjects] = useState<Project[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [shots, setShots] = useState<Shot[]>([]);
  const [selectedShot, setSelectedShot] = useState<Shot | null>(null);
  const [error, setError] = useState("");
  const [loadState, setLoadState] = useState<DashboardLoadState>("loading");
  const [seedLoading, setSeedLoading] = useState(false);
  const [seedError, setSeedError] = useState("");
  const [renamingProjectId, setRenamingProjectId] = useState<string | null>(null);
  const [resettingStorage, setResettingStorage] = useState(false);
  const [creatingCharacterProjectId, setCreatingCharacterProjectId] = useState<string | null>(null);
  const [deletingCharacterId, setDeletingCharacterId] = useState<string | null>(null);
  const [updatingCharacterId, setUpdatingCharacterId] = useState<string | null>(null);
  const [creatingSceneProjectId, setCreatingSceneProjectId] = useState<string | null>(null);
  const [deletingSceneId, setDeletingSceneId] = useState<string | null>(null);
  const [creatingShotSceneId, setCreatingShotSceneId] = useState<string | null>(null);
  const [deletingShot, setDeletingShot] = useState(false);
  const [exportingProjectId, setExportingProjectId] = useState<string | null>(null);
  const [importingStorage, setImportingStorage] = useState(false);
  const [importPreview, setImportPreview] = useState<ImportPreview | null>(null);
  const [importStatusMessage, setImportStatusMessage] = useState("");
  const importFileInputRef = useRef<HTMLInputElement | null>(null);

  const isReadOnly = user?.role === "viewer";
  const selectedScene = selectedShot ? scenes.find((scene) => scene.id === selectedShot.scene_id) ?? null : null;

  async function loadData() {
    setLoadState("loading");
    setError("");

    try {
      const data = await loadDashboardData();

      setProjects(data.projects);
      setCharacters(data.characters);
      setScenes(data.scenes);
      setShots(data.shots);

      if (data.projects.length === 0) {
        setLoadState("empty");
      } else {
        setLoadState("success");
        setSeedError("");
      }

      if (selectedShot) {
        const updatedSelected = data.shots.find((shot: Shot) => shot.id === selectedShot.id) || null;
        setSelectedShot(updatedSelected);
      }
    } catch {
      setError("No se pudieron cargar los datos");
      setLoadState("error");
    }
  }

  useEffect(() => {
    void hydrateSession();
  }, [hydrateSession]);

  useEffect(() => {
    if (user) {
      void loadData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  async function handleUpdateShot(updatedShot: Shot) {
    try {
      const savedShot = await updateStorageShot(updatedShot);

      const nextShots = shots.map((shot) =>
        shot.id === savedShot.id ? savedShot : shot
      );

      setShots(nextShots);
      setSelectedShot(savedShot);
    } catch {
      setError("No se pudo guardar el shot");
    }
  }

  async function handleCreateShot(sceneId: string) {
    setError("");
    setCreatingShotSceneId(sceneId);

    try {
      await createStorageShot(sceneId);
      await loadData();
    } catch {
      setError("No se pudo crear el shot");
    } finally {
      setCreatingShotSceneId(null);
    }
  }

  async function handleCreateScene(projectId: string) {
    setError("");
    setCreatingSceneProjectId(projectId);

    try {
      await createStorageScene(projectId);
      await loadData();
    } catch {
      setError("No se pudo crear la escena");
    } finally {
      setCreatingSceneProjectId(null);
    }
  }

  async function handleCreateCharacter(project: Project, nextName: string) {
    const normalizedName = nextName.trim();
    if (!normalizedName) {
      setError("El nombre del personaje no puede estar vacío");
      return;
    }

    setError("");
    setCreatingCharacterProjectId(project.id);

    try {
      await createStorageCharacter(project.id, normalizedName);
      await loadData();
    } catch (error) {
      const backendMessage = getBackendErrorMessage(error);
      setError(backendMessage ? `No se pudo crear el personaje: ${backendMessage}` : "No se pudo crear el personaje");
    } finally {
      setCreatingCharacterProjectId(null);
    }
  }

  async function handleDeleteCharacter(characterId: string) {
    const normalizedCharacterId = characterId.trim();
    if (!normalizedCharacterId) {
      setError("ID de personaje inválido");
      return;
    }

    setError("");
    setDeletingCharacterId(normalizedCharacterId);
    setCharacters((previous) => previous.filter((character) => character.id !== normalizedCharacterId));

    try {
      await deleteStorageCharacter(normalizedCharacterId);
      await loadData();
    } catch (error) {
      const backendMessage = getBackendErrorMessage(error);
      setError(backendMessage ? `No se pudo eliminar el personaje: ${backendMessage}` : "No se pudo eliminar el personaje");
      await loadData();
    } finally {
      setDeletingCharacterId(null);
    }
  }

  async function handleUpdateCharacter(
    characterId: string,
    name: string,
    seed: number,
    references: string[]
  ): Promise<void> {
    const normalizedName = name.trim();

    if (!normalizedName) {
      setError("El nombre del personaje no puede estar vacío");
      return;
    }

    const normalizedSeedInput = Number(seed);
    if (!Number.isFinite(normalizedSeedInput)) {
      setError("El seed_master del personaje debe ser numérico");
      return;
    }

    const normalizedSeed = Math.trunc(normalizedSeedInput);

    if (!Array.isArray(references)) {
      setError("Las referencias del personaje deben ser una lista");
      return;
    }

    const normalizedReferenceImages = references
      .filter((item): item is string => typeof item === "string")
      .map((item) => item.trim())
      .filter((item) => item.length > 0);

    setError("");
    setUpdatingCharacterId(characterId);

    try {
      await updateStorageCharacter(characterId, {
        name: normalizedName,
        seed_master: normalizedSeed,
        reference_images: normalizedReferenceImages,
      });
      await loadData();
    } catch (error) {
      const backendMessage = getBackendErrorMessage(error);
      setError(backendMessage ? `No se pudo actualizar el personaje: ${backendMessage}` : "No se pudo actualizar el personaje");
    } finally {
      setUpdatingCharacterId(null);
    }
  }

  async function handleRenameProject(project: Project, nextTitle: string) {
    const normalizedTitle = nextTitle.trim();
    if (!normalizedTitle) {
      setError("El título del proyecto no puede estar vacío");
      return;
    }

    setError("");
    setRenamingProjectId(project.id);

    try {
      await renameStorageProject(project.id, normalizedTitle);
      await loadData();
    } catch {
      setError("No se pudo renombrar el proyecto");
    } finally {
      setRenamingProjectId(null);
    }
  }

  async function handleDeleteScene(sceneId: string) {
    setError("");
    setDeletingSceneId(sceneId);

    try {
      await deleteStorageScene(sceneId);

      if (selectedShot && selectedShot.scene_id === sceneId) {
        setSelectedShot(null);
      }

      await loadData();
    } catch {
      setError("No se pudo eliminar la escena");
    } finally {
      setDeletingSceneId(null);
    }
  }

  async function handleResetStorage() {
    const confirmation = window.prompt(
      "Esta accion vacia el storage activo completo. Escribe RESET para confirmar."
    );

    if (confirmation !== "RESET") {
      return;
    }

    setError("");
    setResettingStorage(true);

    try {
      await resetStorageData();
      setSelectedShot(null);
      await loadData();
    } catch {
      setError("No se pudo resetear el storage activo");
    } finally {
      setResettingStorage(false);
    }
  }

  async function handleDeleteShot(shotId: string) {
    setError("");
    setDeletingShot(true);

    try {
      await deleteStorageShot(shotId);

      if (selectedShot && selectedShot.id === shotId) {
        setSelectedShot(null);
      }

      await loadData();
    } catch {
      setError("No se pudo eliminar el shot");
    } finally {
      setDeletingShot(false);
    }
  }

  async function handleInitializeStorage() {
    setSeedLoading(true);
    setSeedError("");

    try {
      await seedStorageData();
      await loadData();
    } catch {
      setSeedError("No se pudo inicializar Storage con datos demo");
      setLoadState("empty");
    } finally {
      setSeedLoading(false);
    }
  }

  async function handleExportProject(project: Project) {
    setError("");
    setExportingProjectId(project.id);

    try {
      const exportPayload = await exportStorageData();
      const fileNameBase = project.title.trim() || project.id;
      const safeFileNameBase = fileNameBase.replace(/[^a-zA-Z0-9-_]+/g, "_");
      const blob = new Blob([JSON.stringify(exportPayload, null, 2)], {
        type: "application/json;charset=utf-8",
      });
      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = `${safeFileNameBase}_export.json`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(objectUrl);
    } catch {
      setError("No se pudo exportar el proyecto activo");
    } finally {
      setExportingProjectId(null);
    }
  }

  function handleImportProject() {
    setError("");
    setImportStatusMessage("");
    setImportPreview(null);

    const importInput = importFileInputRef.current;
    if (!importInput) {
      setError("No se pudo abrir el selector de archivos");
      return;
    }

    importInput.value = "";
    importInput.click();
  }

  async function handleImportFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0] ?? null;
    event.target.value = "";

    if (!selectedFile) {
      return;
    }

    setError("");
    setImportStatusMessage("");
    setImportPreview(null);
    setImportingStorage(true);

    try {
      if (!selectedFile.name.toLowerCase().endsWith(".json")) {
        throw new Error("IMPORT_INVALID_FILE");
      }

      const fileContent = await selectedFile.text();
      if (fileContent.trim() === "") {
        throw new Error("IMPORT_EMPTY_FILE");
      }

      let parsedContent: unknown;
      try {
        parsedContent = JSON.parse(fileContent);
      } catch {
        throw new Error("IMPORT_INVALID_JSON");
      }

      const payload = normalizeStorageImportPayload(parsedContent);
      setImportPreview({
        fileName: selectedFile.name,
        projectLabel: getImportProjectLabel(payload.project),
        counts: {
          characters: payload.characters.length,
          sequences: payload.sequences.length,
          scenes: payload.scenes.length,
          shots: payload.shots.length,
        },
        payload,
      });
      setImportStatusMessage("Vista previa lista. Confirma la importacion para continuar.");
    } catch (error) {
      const backendMessage = getBackendErrorMessage(error);
      if (backendMessage) {
        setError(`No se pudo importar el proyecto: ${backendMessage}`);
        return;
      }

      if (error instanceof Error) {
        if (error.message === "IMPORT_EMPTY_FILE") {
          setError("El archivo seleccionado esta vacio");
          return;
        }

        if (error.message === "IMPORT_INVALID_JSON") {
          setError("El archivo no contiene un JSON valido");
          return;
        }

        if (error.message === "IMPORT_INVALID_FILE") {
          setError("Selecciona un archivo .json valido");
          return;
        }

        if (error.message === "IMPORT_INCOMPATIBLE_FORMAT") {
          setError("El JSON no tiene un formato compatible para importar");
          return;
        }
      }

      setError("No se pudo importar el proyecto");
    } finally {
      setImportingStorage(false);
    }
  }

  function handleCancelImport() {
    setImportPreview(null);
    setImportingStorage(false);
    setImportStatusMessage("");
  }

  async function handleConfirmImport() {
    if (!importPreview) return;

    setImportingStorage(true);
    setImportStatusMessage("Importando proyecto...");

    try {
      await importStorageData(importPreview.payload, "replace");
      setImportPreview(null);
      setImportStatusMessage("Importacion exitosa");
      await loadData();
    } catch (error) {
      const backendMessage = getBackendErrorMessage(error);
      setError(`Error al confirmar la importacion: ${backendMessage || "error en el servidor"}`);
    } finally {
      setImportingStorage(false);
    }
  }

  if (!sessionReady) {
    return <LoginScreen loading={true} error="" onLogin={login} />;
  }

  if (!user) {
    return <LoginScreen loading={sessionLoading} error={loginError} onLogin={login} />;
  }

  return (
    <div className="min-h-screen bg-[#fafafa] text-gray-900 font-sans p-6 md:p-10">
      <input
        ref={importFileInputRef}
        type="file"
        accept=".json,application/json"
        onChange={handleImportFileChange}
        style={{ display: "none" }}
      />

      <div className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-gray-200 bg-white px-4 py-3 shadow-sm">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-gray-500">CINE AI PLATFORM</div>
          <div className="text-sm text-gray-700">
            {user.email} <span className="text-gray-400">·</span> <span className="font-semibold">{user.role}</span>
          </div>
        </div>
        <button
          type="button"
          onClick={() => void logout()}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
        >
          Cerrar sesion
        </button>
      </div>

      {isReadOnly ? (
        <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Modo lectura activo para este rol.
        </div>
      ) : null}

      <div className={isReadOnly ? "pointer-events-none select-none opacity-70" : ""}>
        <h1>Cine AI Platform</h1>
        <h2>Proyectos</h2>

        {error ? <p>{error}</p> : null}
        {importStatusMessage ? <p>{importStatusMessage}</p> : null}

        {/* Modal de Importación (Misión 15C) */}
        {importPreview && (
          <ImportConfirmationModal
            importPreview={importPreview}
            onConfirm={handleConfirmImport}
            onCancel={handleCancelImport}
            importingStorage={importingStorage}
          />
        )}

        {importStatusMessage && !importPreview ? (
          <div className="mb-6 px-4 py-3 bg-green-50 text-green-700 text-sm rounded-xl border border-green-100 animate-in slide-in-from-top-4 duration-300">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              {importStatusMessage}
            </div>
          </div>
        ) : null}

        {loadState === "loading" ? <p>Cargando datos...</p> : null}
        {loadState === "empty" ? (
          <ProjectEmptyState
            onSeedDemo={handleInitializeStorage}
            seedLoading={seedLoading}
            onImportProject={handleImportProject}
            importingStorage={importingStorage}
            seedError={seedError}
          />
        ) : null}

        {loadState === "success" ? (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 360px",
              gap: 24,
              alignItems: "start",
            }}
          >
            <div>
              {projects.map((project) => {
                const projectCharacters = characters.filter((character) => character.project_id === project.id);
                const projectScenes = scenes.filter((scene) => scene.project_id === project.id);

                return (
                  <ProjectCard
                    key={`${project.id}:${project.title}`}
                    project={project}
                    characters={projectCharacters}
                    scenes={projectScenes}
                    shots={shots}
                    selectedShotId={selectedShot ? selectedShot.id : null}
                    onSelectShot={(s) => setSelectedShot(s)}
                    onRenameProject={handleRenameProject}
                    renamingProjectId={renamingProjectId}
                    onResetStorage={handleResetStorage}
                    resettingStorage={resettingStorage}
                    onExportProject={handleExportProject}
                    exportingProjectId={exportingProjectId}
                    onImportProject={handleImportProject}
                    importingStorage={importingStorage}
                    onAddCharacterToProject={handleCreateCharacter}
                    creatingCharacterProjectId={creatingCharacterProjectId}
                    onDeleteCharacter={handleDeleteCharacter}
                    deletingCharacterId={deletingCharacterId}
                    onUpdateCharacter={handleUpdateCharacter}
                    updatingCharacterId={updatingCharacterId}
                    onAddSceneToProject={handleCreateScene}
                    creatingSceneProjectId={creatingSceneProjectId}
                    onDeleteScene={handleDeleteScene}
                    deletingSceneId={deletingSceneId}
                    onAddShotToScene={handleCreateShot}
                    creatingShotSceneId={creatingShotSceneId}
                    onDeleteShot={async (shotId) => {
                      const shotToDelete = shots.find((shot) => shot.id === shotId);
                      if (!shotToDelete) {
                        return;
                      }

                      await handleDeleteShot(shotToDelete.id);
                    }}
                    deletingShot={deletingShot}
                  />
                );
              })}
            </div>

            <div className="space-y-6">
              <ShotBuilderPanel
                shot={selectedShot}
                onUpdateShot={handleUpdateShot}
                onDeleteShot={() => selectedShot && handleDeleteShot(selectedShot.id)}
                deletingShot={deletingShot}
              />

              <ShotSemanticContextSummary
                selectedShot={selectedShot}
                selectedScene={selectedScene}
              />
            </div>
          </div>
        ) : null}

        {loadState !== "loading" ? <SequenceExecutionPanel defaultProjectId={projects[0]?.id} /> : null}
      </div>

      {loadState !== "loading" ? (
        <SemanticContextPanel
          defaultProjectId={projects[0]?.id}
          scenes={scenes}
          selectedShot={selectedShot}
          isReadOnly={isReadOnly}
        />
      ) : null}
    </div>
  );
}

export default App;
