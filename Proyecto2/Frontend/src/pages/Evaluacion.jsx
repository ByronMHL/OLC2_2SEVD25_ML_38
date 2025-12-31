import { useState } from "react";
import { getClusteringEvaluation, evaluateKMeansModel, evaluateHierarchicalModel, evaluateTextKMeansModel, evaluateAutoKModel } from "../../service/Conexion/ComunicacionBack";

export default function Evaluacion() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [errors, setErrors] = useState([]);
  const [singleEval, setSingleEval] = useState(null);

  const loadAll = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await getClusteringEvaluation();
      if (!res.success) {
        setError(res.error || "Error al evaluar clustering");
        setEvaluations([]);
        setErrors(res.details || []);
        return;
      }
      setEvaluations(res.evaluations || []);
      setErrors(res.errors || []);
    } catch (e) {
      setError(e?.error || e?.message || "Error al evaluar clustering");
      setEvaluations([]);
    } finally {
      setIsLoading(false);
    }
  };

  const runSingle = async (fn) => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await fn();
      if (!res.success) {
        setError(res.error || "Error en la evaluación del modelo");
        setSingleEval(null);
        return;
      }
      setSingleEval(res.evaluation || null);
    } catch (e) {
      setError(e?.error || e?.message || "Error en la evaluación del modelo");
      setSingleEval(null);
    } finally {
      setIsLoading(false);
    }
  };

  const MetricCard = ({ title, value }) => (
    <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-4 text-center">
      <div className="text-slate-300 text-sm">{title}</div>
      <div className="text-slate-100 text-2xl font-bold">{value ?? "--"}</div>
    </div>
  );

  return (
    <div className="w-full px-2 md:px-6 py-6">
      <div className="mb-6 text-center">
        <h1 className="text-2xl md:text-3xl font-semibold text-white">Evaluación de Clustering</h1>
      </div>

      <div className="mb-4 flex flex-wrap items-center justify-center gap-2">
        <button onClick={loadAll} disabled={isLoading} className="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60">
          {isLoading ? "Cargando..." : "Evaluar todos"}
        </button>
        <button onClick={() => runSingle(evaluateKMeansModel)} disabled={isLoading} className="inline-flex items-center rounded-md bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-600 disabled:opacity-60">
          {isLoading ? "Cargando..." : "Evaluar K-Means"}
        </button>
        <button onClick={() => runSingle(evaluateHierarchicalModel)} disabled={isLoading} className="inline-flex items-center rounded-md bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-600 disabled:opacity-60">
          {isLoading ? "Cargando..." : "Evaluar Hierarchical"}
        </button>
        <button onClick={() => runSingle(evaluateTextKMeansModel)} disabled={isLoading} className="inline-flex items-center rounded-md bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-600 disabled:opacity-60">
          {isLoading ? "Cargando..." : "Evaluar Text TF-IDF"}
        </button>
        <button onClick={() => runSingle(evaluateAutoKModel)} disabled={isLoading} className="inline-flex items-center rounded-md bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-600 disabled:opacity-60">
          {isLoading ? "Cargando..." : "Evaluar Auto-K"}
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 text-red-800 px-4 py-3">{String(error)}</div>
      )}

      {/* Evaluación por modelo (individual) */}
      {singleEval && (
        <div className="mb-6 rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-100">{singleEval.model}</h2>
            <span className="text-slate-300 text-sm">Clusters: {singleEval.n_clusters ?? "--"}</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <MetricCard title="Silhouette" value={singleEval.silhouette_score != null ? Number(singleEval.silhouette_score).toFixed(4) : "--"} />
            <MetricCard title="Davies-Bouldin" value={singleEval.davies_bouldin_score != null ? Number(singleEval.davies_bouldin_score).toFixed(4) : "--"} />
            <MetricCard title="Calinski-Harabasz" value={singleEval.calinski_harabasz_score != null ? Number(singleEval.calinski_harabasz_score).toFixed(2) : "--"} />
          </div>
        </div>
      )}

      {/* Evaluaciones agregadas */}
      {evaluations.length > 0 && (
        <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5">
          <div className="mb-3">
            <h2 className="text-lg font-semibold text-slate-100">Evaluaciones de modelos</h2>
            <p className="text-sm text-slate-300">Métricas internas por modelo entrenado</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {evaluations.map((ev, idx) => (
              <div key={idx} className="rounded-lg border border-slate-700 bg-slate-800/50 p-4">
                <div className="flex items-center justify-between">
                  <div className="text-slate-100 font-medium">{ev.model}</div>
                  <div className="text-slate-300 text-sm">Clusters: {ev.n_clusters ?? "--"}</div>
                </div>
                <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <MetricCard title="Silhouette" value={ev.silhouette_score != null ? Number(ev.silhouette_score).toFixed(4) : "--"} />
                  <MetricCard title="Davies-Bouldin" value={ev.davies_bouldin_score != null ? Number(ev.davies_bouldin_score).toFixed(4) : "--"} />
                  <MetricCard title="Calinski-Harabasz" value={ev.calinski_harabasz_score != null ? Number(ev.calinski_harabasz_score).toFixed(2) : "--"} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Errores informativos */}
      {errors.length > 0 && (
        <div className="mt-6 rounded-xl border border-slate-700 bg-slate-900/40 shadow-md p-4">
          <div className="text-slate-100 font-medium mb-2">Notas</div>
          <ul className="text-sm text-slate-300 list-disc pl-5">
            {errors.map((er, idx) => (
              <li key={idx}>{er.model ? `${er.model}: ${er.error}` : String(er)}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
