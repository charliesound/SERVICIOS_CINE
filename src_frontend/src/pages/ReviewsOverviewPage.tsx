import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

interface ReviewItem {
  review_id: string;
  title: string;
  status: string;
  created_at: string;
}

const ReviewsOverviewPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/reviews/projects/${projectId}`)
      .then(r => r.json())
      .then(data => setReviews(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return <div className="p-20 text-center">Cargando revisiones...</div>;

  return (
    <div className="p-6">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pipeline de Revisión</h1>
          <p className="text-gray-500">Gestión de feedback y aprobaciones industriales.</p>
        </div>
        <div className="text-xs font-mono bg-gray-100 p-2 rounded">PROJECT_ID: {projectId}</div>
      </header>

      <div className="bg-white shadow-xl rounded-2xl overflow-hidden border border-gray-100">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">Activo / Título</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">Estado de Gobernanza</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">Creación</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-400 uppercase tracking-widest">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {reviews.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-20 text-center text-gray-400 italic">No hay revisiones activas para este proyecto.</td>
              </tr>
            ) : (
              reviews.map(r => (
                <tr key={r.review_id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-bold text-gray-900">{r.title}</div>
                    <div className="text-[10px] text-gray-400 font-mono">{r.review_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-[10px] leading-5 font-bold rounded-full uppercase tracking-tighter ${
                      r.status === 'approved' ? 'bg-green-100 text-green-800' : 
                      r.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-[11px] text-gray-500">
                    {new Date(r.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link to={`/projects/${projectId}/reviews/${r.review_id}`} className="text-indigo-600 hover:text-indigo-900 font-bold">
                      Gestionar →
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReviewsOverviewPage;
