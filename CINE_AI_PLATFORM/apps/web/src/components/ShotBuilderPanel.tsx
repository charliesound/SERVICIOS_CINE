import { useEffect, useState } from "react";

import type { Shot } from "../types/shot";

type ShotBuilderPanelProps = {
  shot: Shot | null;
  onUpdateShot: (updatedShot: Shot) => void;
  onDeleteShot: (shot: Shot) => void;
  deletingShot: boolean;
};

export default function ShotBuilderPanel({ shot, onUpdateShot, onDeleteShot, deletingShot }: ShotBuilderPanelProps) {
  const [form, setForm] = useState<Shot | null>(shot);

  useEffect(() => {
    setForm(shot);
  }, [shot]);

  if (!form) {
    return (
      <div className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-gray-950">Shot Builder</h3>
            <p className="mt-1 text-sm text-gray-500">Selecciona un shot para ver y editar sus parametros.</p>
          </div>
          <div className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
            Sin seleccion
          </div>
        </div>
      </div>
    );
  }

  function updateField<K extends keyof Shot>(field: K, value: Shot[K]) {
    if (form) {
      setForm({
        ...form,
        [field]: value,
      });
    }
  }

  function handleApply() {
    if (form) {
      onUpdateShot(form);
    }
  }

  function handleDelete() {
    if (!form) {
      return;
    }

    const confirmed = window.confirm("¿Seguro que quieres eliminar este plano?");
    if (!confirmed) {
      return;
    }

    onDeleteShot(form);
  }

  return (
    <div className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-gray-100 pb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-950">Shot Builder</h3>
          <p className="mt-1 text-sm text-gray-500">Edita el plano seleccionado y aplica cambios al proyecto activo.</p>
        </div>
        <div className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
          {form.id}
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-gray-500">Shot ID</div>
          <div className="mt-2 font-medium text-gray-900">{form.id}</div>
        </div>
        <div className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-gray-500">Scene ID</div>
          <div className="mt-2 font-medium text-gray-900">{form.scene_id}</div>
        </div>
      </div>

      <div className="mt-5 space-y-4">
        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-gray-700">Tipo</span>
          <input
            type="text"
            value={form.type}
            onChange={(e) => updateField("type", e.target.value)}
            className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-gray-700">Workflow</span>
          <input
            type="text"
            value={form.workflow_key}
            onChange={(e) => updateField("workflow_key", e.target.value)}
            className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-gray-700">Prompt</span>
          <textarea
            value={form.prompt}
            onChange={(e) => updateField("prompt", e.target.value)}
            rows={4}
            className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-gray-700">Negative prompt</span>
          <textarea
            value={form.negative_prompt || ""}
            onChange={(e) => updateField("negative_prompt", e.target.value)}
            rows={3}
            className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
          />
        </label>

        <div className="grid gap-4 sm:grid-cols-3">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-gray-700">Seed</span>
            <input
              type="number"
              value={form.seed}
              onChange={(e) => updateField("seed", Number(e.target.value))}
              className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            />
          </label>

          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-gray-700">CFG</span>
            <input
              type="number"
              step="0.1"
              value={form.cfg}
              onChange={(e) => updateField("cfg", Number(e.target.value))}
              className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            />
          </label>

          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-gray-700">Steps</span>
            <input
              type="number"
              value={form.steps}
              onChange={(e) => updateField("steps", Number(e.target.value))}
              className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            />
          </label>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-gray-500">Referencias</div>
          <div className="mt-2">{form.refs.length > 0 ? form.refs.join(", ") : "Sin refs"}</div>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          onClick={handleApply}
          className="rounded-xl bg-gray-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-gray-800"
        >
          Aplicar cambios
        </button>

        <button
          type="button"
          onClick={handleDelete}
          disabled={deletingShot}
          className="rounded-xl border border-red-200 bg-white px-4 py-3 text-sm font-semibold text-red-700 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {deletingShot ? "Eliminando..." : "Eliminar"}
        </button>
      </div>
    </div>
  );
}
