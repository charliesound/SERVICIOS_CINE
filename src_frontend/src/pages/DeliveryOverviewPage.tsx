import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

interface DeliverableItem {
  deliverable_id: string;
  source_review_id: string;
  title: string;
  asset_type: string;
  created_at: string;
}

const DeliveryOverviewPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [deliverables, setDeliverables] = useState<DeliverableItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/delivery/projects/${projectId}/deliverables`)
      .then(r => r.json())
      .then(data => setDeliverables(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return <div className="p-20 text-center animate-pulse">Cargando entregables finales...</div>;

  return (
    <div className="p-6">
      <header className="mb-10 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Librería de Entregables</h1>
          <p className="text-gray-500 text-lg">Archivos aprobados y trazables listos para post-producción final.</p>
        </div>
      </header>

      {deliverables.length === 0 ? (
        <div className="bg-gray-50 rounded-3xl p-20 text-center border-2 border-dashed border-gray-200">
           <div className="text-64 mb-4">📦</div>
           <h3 className="text-xl font-bold text-gray-600">No hay entregables aprobados</h3>
           <p className="text-gray-400 mt-2">Los entregables aparecen aquí automáticamente tras la aprobación de una revisión.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {deliverables.map(d => (
            <div key={d.deliverable_id} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:scale-[1.02] transition-transform group">
              <div className="aspect-video bg-gray-900 relative items-center justify-center flex">
                 <div className="text-indigo-400 font-mono text-[10px] opacity-30">PRORES_422_MASTER</div>
                 <div className="absolute top-4 right-4 px-3 py-1 bg-green-500 text-white text-[10px] font-black rounded-full uppercase shadow-lg shadow-green-200">Oficial</div>
              </div>
              <div className="p-6">
                <h3 className="font-bold text-gray-900 truncate text-lg group-hover:text-indigo-600 transition-colors">{d.title}</h3>
                <p className="text-[10px] text-gray-400 mt-1 mb-4 font-mono">ID: {d.deliverable_id}</p>
                <div className="flex justify-between items-center text-xs text-gray-400 border-t border-gray-50 pt-4">
                   <div className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-green-400"></span>
                      <span>Link: {d.source_review_id.slice(0,8)}</span>
                   </div>
                   <span>{new Date(d.created_at).toLocaleDateString()}</span>
                </div>
                <div className="mt-6 flex gap-2">
                   <Link 
                    to={`/projects/${projectId}/delivery/${d.deliverable_id}`}
                    className="flex-1 text-center bg-gray-950 text-white py-3 rounded-xl text-xs font-black hover:bg-black uppercase tracking-widest transition"
                   >
                     Detalles
                   </Link>
                   <button className="w-12 bg-gray-100 text-gray-600 rounded-xl hover:bg-gray-200 transition flex items-center justify-center">
                      ⬇️
                   </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DeliveryOverviewPage;
