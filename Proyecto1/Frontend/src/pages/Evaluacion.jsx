import { useEffect, useState } from "react";
// No llamamos al endpoint de entrenamiento aquí.

export default function Evaluacion() {
  const [metrics, setMetrics] = useState([
    { key: "accuracy", title: "Exactitud", value: "--%" },
    { key: "precision", title: "Precisión", value: "--%" },
    { key: "recall", title: "Recall", value: "--%" },
    { key: "f1", title: "F1-Score", value: "--%" },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [alert, setAlert] = useState(null);
  const [table, setTable] = useState({ columns: [], rows: [] });

  const loadResults = () => {
    try {
      setIsLoading(true);
      setAlert(null);
      const raw = localStorage.getItem("trainingResults");
      if (!raw) {
        setAlert({ type: "error", message: "No hay resultados disponibles. Ejecute el entrenamiento en Carga Masiva." });
        return; // El finally actualizará isLoading
      }
      const res = JSON.parse(raw);
      const m = res?.metrics || {};
      setMetrics([
        { key: "accuracy", title: "Exactitud", value: m.accuracy != null ? `${(m.accuracy * 100).toFixed(2)}%` : "--%" },
        { key: "precision", title: "Precisión", value: m.precision != null ? `${(m.precision * 100).toFixed(2)}%` : "--%" },
        { key: "recall", title: "Recall", value: m.recall != null ? `${(m.recall * 100).toFixed(2)}%` : "--%" },
        { key: "f1", title: "F1-Score", value: m.f1 != null ? `${(m.f1 * 100).toFixed(2)}%` : "--%" },
      ]);
      if (Array.isArray(res?.results?.rows) && Array.isArray(res?.results?.columns)) {
        setTable({ columns: res.results.columns, rows: res.results.rows });
      } else {
        setTable({ columns: [], rows: [] });
      }
      setAlert({ type: "success", message: res?.message || "Resultados cargados." });
    } catch (err) {
      setAlert({ type: "error", message: "Error al leer resultados almacenados." });
    } finally {
      setIsLoading(false);
    }
  };

  // Cargar automáticamente los resultados guardados al montar la página
  useEffect(() => {
    const raw = localStorage.getItem("trainingResults");
    if (raw) {
      try {
        const res = JSON.parse(raw);
        const m = res?.metrics || {};
        setMetrics([
          { key: "accuracy", title: "Exactitud", value: m.accuracy != null ? `${(m.accuracy * 100).toFixed(2)}%` : "--%" },
          { key: "precision", title: "Precisión", value: m.precision != null ? `${(m.precision * 100).toFixed(2)}%` : "--%" },
          { key: "recall", title: "Recall", value: m.recall != null ? `${(m.recall * 100).toFixed(2)}%` : "--%" },
          { key: "f1", title: "F1-Score", value: m.f1 != null ? `${(m.f1 * 100).toFixed(2)}%` : "--%" },
        ]);
        if (Array.isArray(res?.results?.rows) && Array.isArray(res?.results?.columns)) {
          setTable({ columns: res.results.columns, rows: res.results.rows });
        } else {
          setTable({ columns: [], rows: [] });
        }
        setAlert({ type: "success", message: res?.message || "Resultados listos." });
      } catch (err) {
        // Si falla el parse, no romper la vista
      }
    }
  }, []);

  return (
    <div className="w-full px-2 md:px-6 py-6">
      <div className="mb-6 text-center">
        <h1 className="text-2xl md:text-3xl font-semibold text-white">Evaluación de Rendimiento</h1>
      </div>
      <div className="mb-4 flex items-center justify-center">
        <button
          onClick={loadResults}
          disabled={isLoading}
          className="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
        >
          {isLoading ? "Cargando..." : "Refrescar resultados"}
        </button>
      </div>

      {alert && (
        <div className={alert.type === "success" ? "mb-4 rounded-lg border border-green-200 bg-green-50 text-green-800 px-4 py-3" : "mb-4 rounded-lg border border-red-200 bg-red-50 text-red-800 px-4 py-3"}>
          {alert.message}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m) => (
          <div
            key={m.key}
            className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5 flex flex-col items-center justify-center min-h-[140px]"
          >
            <div className="text-3xl md:text-4xl font-bold text-slate-100">{m.value}</div>
            <div className="mt-2 text-sm md:text-base text-slate-300">{m.title}</div>
          </div>
        ))}
      </div>

      {/* Tabla de resultados (mock si backend la envía) */}
      {table.columns.length > 0 && (
        <div className="mt-6 rounded-xl border border-slate-700 bg-slate-900/50 shadow-md overflow-auto">
          <table className="min-w-full text-left text-sm text-slate-200">
            <thead className="bg-slate-800">
              <tr>
                {table.columns.map((col) => (
                  <th key={col} className="px-4 py-2 font-medium text-slate-100 border-b border-slate-700">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.rows.map((row, idx) => (
                <tr key={idx} className="border-b border-slate-800">
                  {table.columns.map((col) => (
                    <td key={col} className="px-4 py-2">{row[col]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
