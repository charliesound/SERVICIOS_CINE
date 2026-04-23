import React from 'react';
import { useParams, Link } from 'react-router-dom';

const DeliverableDetailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string; deliverableId: string }>();

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <nav className="mb-4">
        <Link to={`/projects/${projectId}/delivery`} className="text-indigo-600 hover:underline">← Volver a Entregables</Link>
      </nav>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-8 border-b border-gray-50">
          <div className="flex justify-between items-start mb-6">
            <div>
              <span className="text-xs font-bold text-indigo-500 uppercase tracking-widest">Entregable Final</span>
              <h1 className="text-3xl font-bold mt-1">Escena_01_Final_Master.mp4</h1>
            </div>
            <button className="bg-indigo-600 text-white px-6 py-2 rounded-full font-bold shadow-lg hover:shadow-indigo-200 transition">
              Descargar Prores 422
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="bg-gray-50 p-4 rounded-xl">
              <span className="block text-[10px] uppercase text-gray-400 font-bold mb-1">Source Review</span>
              <Link to={`/projects/${projectId}/reviews/rev_demo_001`} className="text-xs font-mono text-indigo-600 truncate block">rev_demo_001</Link>
            </div>
            <div className="bg-gray-50 p-4 rounded-xl">
              <span className="block text-[10px] uppercase text-gray-400 font-bold mb-1">Tamaño</span>
              <span className="text-xs font-mono">1.2 GB</span>
            </div>
            <div className="bg-gray-50 p-4 rounded-xl">
              <span className="block text-[10px] uppercase text-gray-400 font-bold mb-1">Formato</span>
              <span className="text-xs font-mono">QuickTime</span>
            </div>
            <div className="bg-gray-50 p-4 rounded-xl">
              <span className="block text-[10px] uppercase text-gray-400 font-bold mb-1">Fecha</span>
              <span className="text-xs font-mono">2026-04-13</span>
            </div>
          </div>
        </div>

        <div className="p-8">
           <h3 className="font-bold mb-4">Metadatos de Trazabilidad</h3>
           <div className="bg-gray-900 rounded-xl p-4 font-mono text-xs text-green-400">
             <pre>{`{
  "source_review_id": "rev_demo_001",
  "approval_hash": "8f3e2b1a9c4d5e6f7a8b9c0d1e2f3a4b",
  "pipeline_version": "v1.4.2",
  "render_backend": "still_still",
  "editorial_status": "locked"
}`}</pre>
           </div>
        </div>
      </div>
    </div>
  );
};

export default DeliverableDetailPage;
