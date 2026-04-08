export interface ImportPreviewData {
  fileName: string;
  projectLabel: string;
  counts: {
    characters: number;
    sequences: number;
    scenes: number;
    shots: number;
  };
}

interface ImportConfirmationModalProps {
  importPreview: ImportPreviewData;
  onConfirm: () => void;
  onCancel: () => void;
  importingStorage: boolean;
}

export default function ImportConfirmationModal({
  importPreview,
  onConfirm,
  onCancel,
  importingStorage,
}: ImportConfirmationModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-gray-100 animate-in zoom-in-95 duration-200">
        <div className="p-6 border-b border-gray-100 bg-blue-50/30">
          <div className="flex items-center gap-3 text-blue-600 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <h3 className="font-bold text-lg">Confirmar Importación</h3>
          </div>
          <p className="text-sm text-blue-600/70">Revisa los datos antes de sobrescribir el proyecto actual.</p>
        </div>
        
        <div className="p-6 space-y-6">
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-100 italic text-sm text-gray-600">
            "{importPreview.fileName}" &rarr; <span className="font-bold text-gray-900 not-italic">{importPreview.projectLabel}</span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white border border-gray-100 rounded-xl p-3 flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xs">P</div>
              <div>
                <div className="text-[10px] text-gray-400 uppercase font-bold">Personajes</div>
                <div className="text-sm font-bold">{importPreview.counts.characters}</div>
              </div>
            </div>
            <div className="bg-white border border-gray-100 rounded-xl p-3 flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs">S</div>
              <div>
                <div className="text-[10px] text-gray-400 uppercase font-bold">Secuencias</div>
                <div className="text-sm font-bold">{importPreview.counts.sequences}</div>
              </div>
            </div>
            <div className="bg-white border border-gray-100 rounded-xl p-3 flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-xs">E</div>
              <div>
                <div className="text-[10px] text-gray-400 uppercase font-bold">Escenas</div>
                <div className="text-sm font-bold">{importPreview.counts.scenes}</div>
              </div>
            </div>
            <div className="bg-white border border-gray-100 rounded-xl p-3 flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-xs">L</div>
              <div>
                <div className="text-[10px] text-gray-400 uppercase font-bold">Planos</div>
                <div className="text-sm font-bold">{importPreview.counts.shots}</div>
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-red-50 text-red-700 rounded-xl border border-red-100 text-xs">
            <div className="mt-0.5">⚠️</div>
            <p><strong>Atención:</strong> Esta acción es irreversible. Se eliminará todo el contenido editorial del proyecto actual y será reemplazado por los datos del archivo.</p>
          </div>
        </div>

        <div className="p-6 bg-gray-50/50 flex gap-3 border-t border-gray-100">
          <button 
            onClick={onCancel}
            disabled={importingStorage}
            className="flex-1 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 text-sm font-bold rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button 
            onClick={onConfirm}
            disabled={importingStorage}
            className="flex-[2] px-4 py-2.5 bg-blue-600 text-white text-sm font-bold rounded-xl hover:bg-blue-700 shadow-md shadow-blue-500/20 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {importingStorage ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Importando...</span>
              </>
            ) : (
              <span>Reemplazar y Cargar</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
