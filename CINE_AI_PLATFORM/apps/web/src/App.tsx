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
import ComfyDashboardPanel from "./components/ComfyDashboardPanel";
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
    <div className="min-h-screen px-4 py-6 text-gray-900 md:px-8 md:py-8">
      <input
        ref={importFileInputRef}
        type="file"
        accept=".json,application/json"
        onChange={handleImportFileChange}
        style={{ display: "none" }}
      />

      <div className="mito-shell">
        <div className="mito-panel mb-6 overflow-hidden rounded-[32px] p-5 sm:p-6 md:p-7">
          <div className="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_380px] lg:items-stretch">
            <div className="space-y-4">
              <div>
                <div className="mito-eyebrow">CINE AI PLATFORM</div>
                <h1 className="mt-4 max-w-4xl text-3xl font-semibold tracking-[-0.05em] text-gray-950 md:text-5xl">Panel editorial y operativo</h1>
                <p className="mt-3 max-w-3xl text-sm leading-6 text-[#6a645b] md:text-base">
                  Gestiona proyectos, shots, contexto semantico y seguimiento de ejecuciones desde una sola vista.
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={handleImportProject}
                  className="rounded-full bg-[#1f1b17] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#312a24]"
                >
                  Importar Proyecto
                </button>
                <a
                  href="#comfy-dashboard"
                  className="rounded-full border border-black/10 bg-white px-5 py-3 text-sm font-semibold text-gray-800 transition hover:bg-[#f6f0e7]"
                >
                  Ir a ComfyUI
                </a>
                <a
                  href="#operations-panel"
                  className="rounded-full border border-black/10 bg-white px-5 py-3 text-sm font-semibold text-gray-800 transition hover:bg-[#f6f0e7]"
                >
                  Ir a Operations
                </a>
              </div>

              <div className="flex flex-wrap gap-3">
                <div className="rounded-2xl border border-black/8 bg-[#f7f2ea] px-4 py-3">
                  <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#7b7468]">Sesion</div>
                  <div className="mt-1 text-sm font-medium text-gray-900">{user.email}</div>
                </div>
                <div className="rounded-2xl border border-[#d8b491] bg-[#fff5ea] px-4 py-3">
                  <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#9b6032]">Rol</div>
                  <div className="mt-1 text-sm font-semibold text-[#6b3f1f]">{user.role}</div>
                </div>
                <div className="rounded-2xl border border-black/8 bg-[#f7f2ea] px-4 py-3">
                  <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#7b7468]">Proyectos</div>
                  <div className="mt-1 text-sm font-semibold text-gray-900">{projects.length}</div>
                </div>
                <div className="rounded-2xl border border-black/8 bg-[#f7f2ea] px-4 py-3">
                  <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#7b7468]">Shots</div>
                  <div className="mt-1 text-sm font-semibold text-gray-900">{shots.length}</div>
                </div>
              </div>
            </div>

            <div className="relative overflow-hidden rounded-[28px] border border-black/8 bg-[linear-gradient(145deg,_#171411_0%,_#2b241e_52%,_#8e5a34_100%)] p-5 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
              <div className="absolute -right-10 -top-10 h-36 w-36 rounded-full bg-white/10 blur-2xl" />
              <div className="absolute bottom-0 left-0 h-28 w-full bg-[linear-gradient(180deg,_transparent,_rgba(255,255,255,0.06))]" />
              <div className="relative flex h-full flex-col justify-between gap-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-white/60">Creative Surface</div>
                    <div className="mt-2 text-2xl font-semibold tracking-[-0.04em]">De la idea al shot</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => void logout()}
                    className="rounded-full border border-white/15 bg-white/8 px-4 py-2 text-xs font-semibold text-white transition hover:bg-white/14"
                  >
                    Cerrar sesion
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-2xl border border-white/10 bg-white/8 p-4 backdrop-blur-sm">
                    <div className="text-[11px] uppercase tracking-[0.18em] text-white/55">Scene 01</div>
                    <div className="mt-2 text-sm font-medium text-white">Warm daylight storyboard with continuity cues.</div>
                    <div className="mt-4 h-20 rounded-xl bg-[linear-gradient(135deg,_rgba(255,214,170,0.5),_rgba(255,255,255,0.08))]" />
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/8 p-4 backdrop-blur-sm">
                    <div className="text-[11px] uppercase tracking-[0.18em] text-white/55">Scene 02</div>
                    <div className="mt-2 text-sm font-medium text-white">Editorial review, retries and context in sync.</div>
                    <div className="mt-4 h-20 rounded-xl bg-[linear-gradient(135deg,_rgba(255,255,255,0.14),_rgba(200,111,49,0.48))]" />
                  </div>
                </div>

                <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-black/15 px-4 py-3 text-sm">
                  <div>
                    <div className="text-white/55">Selected flow</div>
                    <div className="mt-1 font-semibold text-white">Projects + Operations + Semantic Context</div>
                  </div>
                  <div className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-[#3a281b]">Live</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {isReadOnly ? (
          <div className="mb-4 rounded-2xl border border-amber-200 bg-[#fff4df] px-4 py-3 text-sm text-amber-900 shadow-sm">
            Modo lectura activo para este rol.
          </div>
        ) : null}

        <div className={isReadOnly ? "pointer-events-none select-none opacity-70" : ""}>
          <section className="mito-panel-soft mb-6 rounded-[32px] p-5 sm:p-6 md:p-7">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <div className="mito-kicker">Workspace</div>
                <h2 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-gray-950 md:text-3xl">Proyectos</h2>
                <p className="mt-3 max-w-3xl text-sm leading-6 text-[#6a645b]">Explora el proyecto activo, organiza personajes y selecciona un shot para editarlo en el panel lateral.</p>
              </div>
              <div className="flex flex-wrap gap-3">
                <div className="rounded-2xl border border-black/8 bg-[#f7f2ea] px-4 py-3 text-sm text-gray-700">
                  <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#7b7468]">Escenas</div>
                  <div className="mt-1 text-lg font-semibold text-gray-900">{scenes.length}</div>
                </div>
                <div className="rounded-2xl border border-black/8 bg-[#f7f2ea] px-4 py-3 text-sm text-gray-700">
                  <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#7b7468]">Personajes</div>
                  <div className="mt-1 text-lg font-semibold text-gray-900">{characters.length}</div>
                </div>
              </div>
            </div>

            {error ? <div className="mt-5 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div> : null}

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
              <div className="mt-5 rounded-2xl border border-green-100 bg-green-50 px-4 py-3 text-sm text-green-700 animate-in slide-in-from-top-4 duration-300">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                  {importStatusMessage}
                </div>
              </div>
            ) : null}

            {loadState === "loading" ? <p className="mt-6 text-sm text-gray-500">Cargando datos...</p> : null}
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
              <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1fr)_380px] xl:items-start">
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

                <div className="space-y-6 xl:sticky xl:top-6">
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
          </section>

        {loadState !== "loading" ? (
          <ComfyDashboardPanel />
        ) : null}

        {loadState !== "loading" ? (
          <section id="operations-panel" className="mito-panel-soft rounded-[32px] p-5 sm:p-6 md:p-7">
            <div className="mb-5">
                <div className="mito-kicker">Operations</div>
                <h2 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-gray-950 md:text-3xl">Sequence plan, render y monitoreo</h2>
                <p className="mt-3 max-w-3xl text-sm leading-6 text-[#6a645b]">Sigue ejecuciones, alertas, webhooks y revision editorial sin salir del panel.</p>
              </div>
              <SequenceExecutionPanel defaultProjectId={projects[0]?.id} />
            </section>
          ) : null}
        </div>

        {loadState !== "loading" ? (
          <section className="mito-panel-soft mt-6 rounded-[32px] p-5 sm:p-6 md:p-7">
            <div className="mb-5">
              <div className="mito-kicker">Context</div>
              <h2 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-gray-950 md:text-3xl">Semantic Context</h2>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-[#6a645b]">Consulta, busca e ingiere contexto semantico para enriquecer escenas y shots del proyecto activo.</p>
            </div>
            <SemanticContextPanel
              defaultProjectId={projects[0]?.id}
              scenes={scenes}
              selectedShot={selectedShot}
              isReadOnly={isReadOnly}
            />
          </section>
        ) : null}
      </div>
    </div>
  );
}

export default App;
