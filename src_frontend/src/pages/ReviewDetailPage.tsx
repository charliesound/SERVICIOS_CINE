import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

interface Comment {
  comment_id: string;
  user_id: string;
  content: string;
  created_at: string;
}

interface ReviewDetail {
  review_id: string;
  project_id: string;
  target_id: string;
  title: string;
  status: string;
  description?: string;
  comments: Comment[];
}

const ReviewDetailPage: React.FC = () => {
  const { projectId, reviewId } = useParams<{ projectId: string; reviewId: string }>();
  const [review, setReview] = useState<ReviewDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [commentText, setCommentText] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchReview();
  }, [reviewId]);

  const fetchReview = async () => {
    try {
      const resp = await fetch(`/api/reviews/${reviewId}`);
      if (resp.ok) {
        setReview(await resp.json());
      }
    } catch (err) {
      console.error("Error fetching review", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (decision: string) => {
    setActionLoading(true);
    try {
      const resp = await fetch(`/api/reviews/${reviewId}/decisions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, note: "Updated from UI" })
      });
      if (resp.ok) {
        await fetchReview();
        alert(`Decisión registrada: ${decision}`);
      }
    } catch (err) {
      console.error("Error making decision", err);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePostComment = async () => {
    if (!commentText.trim()) return;
    setActionLoading(true);
    try {
      const resp = await fetch(`/api/reviews/${reviewId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: commentText })
      });
      if (resp.ok) {
        setCommentText('');
        await fetchReview();
      }
    } catch (err) {
      console.error("Error posting comment", err);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="p-20 text-center animate-pulse">Cargando revisión industrial...</div>;
  if (!review) return <div className="p-20 text-center text-red-500">Revisión no encontrada</div>;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <nav className="mb-4">
        <Link to={`/projects/${projectId}/reviews`} className="text-indigo-600 hover:underline">← Volver a Revisiones</Link>
      </nav>

      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">{review.title}</h1>
          <p className="text-sm text-gray-500">ID: {review.review_id} • Status: <span className="font-bold uppercase">{review.status}</span></p>
        </div>
        <div className="flex gap-2">
           {review.status === 'approved' && (
             <Link to={`/projects/${projectId}/delivery`} className="bg-indigo-100 text-indigo-700 px-4 py-2 rounded-lg font-bold text-sm">
               Ver Entregable Corresponidiente →
             </Link>
           )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="aspect-video bg-black rounded-xl border border-gray-800 flex items-center justify-center overflow-hidden shadow-2xl">
            <div className="text-center text-gray-600">
               <div className="font-mono text-xs mb-2">PROCESSED_ASSET_LAYER</div>
               <div className="text-xl font-bold text-gray-400 italic">VISTA DE MONTAJE</div>
               <div className="mt-4 text-[10px] text-gray-700">{review.target_id}</div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-bold mb-2">Descripción Contextual</h2>
            <p className="text-gray-600 italic">"{review.description || 'Sin descripción adicional.'}"</p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="font-bold text-lg mb-4">Gobernanza de Aprobación</h3>
            <div className="space-y-3">
              <button 
                onClick={() => handleDecision('approve')}
                disabled={actionLoading || review.status === 'approved'}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition disabled:opacity-50"
              >
                {review.status === 'approved' ? 'YA APROBADO' : 'APROBAR ENTREGA'}
              </button>
              <button 
                onClick={() => handleDecision('request_changes')}
                disabled={actionLoading}
                className="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded transition disabled:opacity-50"
              >
                SOLICITAR CAMBIOS
              </button>
              <button 
                onClick={() => handleDecision('reject')}
                disabled={actionLoading}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition disabled:opacity-50"
              >
                RECHAZAR
              </button>
            </div>
            <p className="text-[10px] text-gray-400 mt-4 text-center">
              * La aprobación genera automáticamente un Deliverable oficial con trazabilidad.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col h-[400px]">
            <h3 className="font-bold text-lg mb-4">Feedback Industrial</h3>
            <div className="flex-1 overflow-y-auto mb-4 border-t border-gray-50 pt-4 space-y-4">
              {review.comments.length === 0 ? (
                <div className="text-sm text-gray-500 italic text-center py-10">Sin feedback todavía.</div>
              ) : (
                review.comments.map(c => (
                  <div key={c.comment_id} className="text-xs bg-gray-50 p-2 rounded">
                    <div className="font-bold text-indigo-600 mb-1">{c.user_id}</div>
                    <div className="text-gray-900">{c.content}</div>
                    <div className="text-[9px] text-gray-400 text-right mt-1">{new Date(c.created_at).toLocaleString()}</div>
                  </div>
                ))
              )}
            </div>
            <div className="mt-auto">
              <textarea 
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                placeholder="Escribe feedback técnico..."
                rows={3}
              />
              <button 
                onClick={handlePostComment}
                disabled={actionLoading}
                className="mt-2 w-full bg-indigo-600 text-white py-2 rounded text-sm font-semibold hover:bg-indigo-700 transition disabled:opacity-50"
              >
                Enviar Comentario
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReviewDetailPage;
