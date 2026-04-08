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
      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: 8,
          padding: 16,
          minWidth: 320,
          background: "#fafafa",
        }}
      >
        <h3>Shot Builder</h3>
        <p>Selecciona un shot para ver y editar sus parametros.</p>
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
    <div
      style={{
        border: "1px solid #ccc",
        borderRadius: 8,
        padding: 16,
        minWidth: 320,
        background: "#fafafa",
      }}
    >
      <h3>Shot Builder</h3>

      <div style={{ marginBottom: 12 }}>
        <strong>ID:</strong> {form.id}
      </div>

      <div style={{ marginBottom: 12 }}>
        <strong>Scene ID:</strong> {form.scene_id}
      </div>

      <div style={{ marginBottom: 12 }}>
        <label><strong>Tipo</strong></label>
        <input
          type="text"
          value={form.type}
          onChange={(e) => updateField("type", e.target.value)}
          style={{ width: "100%", marginTop: 6, padding: 8 }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <label><strong>Workflow</strong></label>
        <input
          type="text"
          value={form.workflow_key}
          onChange={(e) => updateField("workflow_key", e.target.value)}
          style={{ width: "100%", marginTop: 6, padding: 8 }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <label><strong>Prompt</strong></label>
        <textarea
          value={form.prompt}
          onChange={(e) => updateField("prompt", e.target.value)}
          rows={4}
          style={{ width: "100%", marginTop: 6, padding: 8 }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <label><strong>Negative prompt</strong></label>
        <textarea
          value={form.negative_prompt || ""}
          onChange={(e) => updateField("negative_prompt", e.target.value)}
          rows={3}
          style={{ width: "100%", marginTop: 6, padding: 8 }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <label><strong>Seed</strong></label>
        <input
          type="number"
          value={form.seed}
          onChange={(e) => updateField("seed", Number(e.target.value))}
          style={{ width: "100%", marginTop: 6, padding: 8 }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <label><strong>CFG</strong></label>
        <input
          type="number"
          step="0.1"
          value={form.cfg}
          onChange={(e) => updateField("cfg", Number(e.target.value))}
          style={{ width: "100%", marginTop: 6, padding: 8 }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <label><strong>Steps</strong></label>
        <input
          type="number"
          value={form.steps}
          onChange={(e) => updateField("steps", Number(e.target.value))}
          style={{ width: "100%", marginTop: 6, padding: 8 }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <strong>Refs:</strong> {form.refs.length > 0 ? form.refs.join(", ") : "Sin refs"}
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <button
          onClick={handleApply}
          style={{
            padding: "10px 14px",
            borderRadius: 6,
            border: "1px solid #2563eb",
            background: "#2563eb",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Aplicar cambios
        </button>

        <button
          type="button"
          onClick={handleDelete}
          disabled={deletingShot}
          style={{
            padding: "10px 14px",
            borderRadius: 6,
            border: "1px solid #b91c1c",
            background: "#ffffff",
            color: "#b91c1c",
            cursor: deletingShot ? "not-allowed" : "pointer",
          }}
        >
          {deletingShot ? "Eliminando..." : "Eliminar"}
        </button>
      </div>
    </div>
  );
}
