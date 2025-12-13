import { useState } from "react";

export default function Evaluacion() {
  const [metrics] = useState([
    { key: "accuracy", title: "Exactitud", value: "--%" },
    { key: "precision", title: "Precisión", value: "--%" },
    { key: "recall", title: "Recall", value: "--%" },
    { key: "f1", title: "F1-Score", value: "--%" },
  ]);

  return (
    <div className="w-full px-2 md:px-6 py-6">
      <div className="mb-6 text-center">
        <h1 className="text-2xl md:text-3xl font-semibold text-white">Evaluación de Rendimiento</h1>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m) => (
          <div
            key={m.key}
            className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5 flex flex-col items-center justify-center min-h-35"
          >
            <div className="text-3xl md:text-4xl font-bold text-slate-100">{m.value}</div>
            <div className="mt-2 text-sm md:text-base text-slate-300">{m.title}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
