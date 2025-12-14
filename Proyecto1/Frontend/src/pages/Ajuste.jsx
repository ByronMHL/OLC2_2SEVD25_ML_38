import { useState } from "react";
import { randomSearch } from "../../service/Conexion/ComunicacionBack";

export default function Ajuste() {
  // Sólo parámetros ajustables: n_iter y cv
  const [nIter, setNIter] = useState(20); // recomendado 10–50, límite 1–200
  const [cv, setCv] = useState(3); // recomendado 3–5, límite 2–10

  const [isTuning, setIsTuning] = useState(false);
  const [alert, setAlert] = useState(null);

  const handleRandomSearch = async () => {
    setAlert(null);
    setIsTuning(true);
    try {
      const params = { n_iter: nIter, cv };
      const res = await randomSearch(params);
      localStorage.setItem("tuningResults", JSON.stringify(res));
      const score = res?.best_score_cv != null ? Number(res.best_score_cv).toFixed(4) : "--";
      setAlert({ type: "success", message: `RandomizedSearchCV completado (F1 CV: ${score})` });
    } catch (err) {
      const msg = typeof err === "string" ? err : err?.error || "Error en RandomizedSearchCV";
      setAlert({ type: "error", message: msg });
    } finally {
      setIsTuning(false);
    }
  };

  return (
    <div className="w-full px-2 md:px-6 py-6">
      <div className="mb-6 text-center">
        <h1 className="text-2xl md:text-3xl font-semibold text-white">Ajuste de Hiperparámetros</h1>
      </div>

      {alert && (
        <div className={alert.type === "success" ? "mb-4 rounded-lg border border-green-200 bg-green-50 text-green-800 px-4 py-3" : "mb-4 rounded-lg border border-red-200 bg-red-50 text-red-800 px-4 py-3"}>
          {alert.message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Columna izquierda: guía y recomendaciones */}
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5">
            <div className="text-slate-100 font-semibold mb-2">Parámetros disponibles</div>
            <ul className="text-slate-300 text-sm list-disc pl-5 space-y-1">
              <li><span className="font-semibold">n_iter</span>: combinaciones a probar (recomendado 10–50, límite 1–200).</li>
              <li><span className="font-semibold">cv</span>: validación cruzada (recomendado 3–5, límite 2–10).</li>
              <li>El resto de hiperparámetros usan valores por defecto y límites seguros.</li>
            </ul>
          </div>
        </div>

        {/* Columna derecha: parámetros del randomized search y botón */}
        <div className="flex flex-col items-stretch lg:items-center justify-start gap-4">
          <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5 w-full">
            <div className="text-slate-100 font-semibold mb-2">Ajustes del RandomizedSearchCV</div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="text-slate-300 text-sm">n_iter</label>
                <input type="number" min={1} max={200} value={nIter} onChange={(e) => setNIter(Math.min(Math.max(1, parseInt(e.target.value) || 1), 200))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                <p className="mt-1 text-xs text-slate-400">Recomendado: 10–50</p>
              </div>
              <div>
                <label className="text-slate-300 text-sm">cv</label>
                <input type="number" min={2} max={10} value={cv} onChange={(e) => setCv(Math.min(Math.max(2, parseInt(e.target.value) || 2), 10))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                <p className="mt-1 text-xs text-slate-400">Recomendado: 3–5</p>
              </div>
            </div>
            <p className="mt-2 text-xs text-slate-400">El criterio de evaluación es F1 (fijo).</p>
          </div>
          <button
            onClick={handleRandomSearch}
            disabled={isTuning}
            className="inline-flex items-center rounded-xl bg-amber-600 px-6 py-4 text-base font-semibold text-white hover:bg-amber-700 disabled:opacity-60 shadow-md"
          >
            {isTuning ? "Buscando (Random)..." : "Ejecutar RandomizedSearchCV"}
          </button>
        </div>
      </div>
    </div>
  );
}
