import { useState } from "react";
import Service from "../../service/Service.js";

export default function Prediccion() {
  // Estados del formulario
  const [promedioActual, setPromedioActual] = useState(0);
  const [asistenciaClases, setAsistenciaClases] = useState(0);
  const [tareasEntregadas, setTareasEntregadas] = useState(0);
  const [participacionClase, setParticipacionClase] = useState(0);
  const [horasEstudio, setHorasEstudio] = useState(0);
  const [promedioEvaluaciones, setPromedioEvaluaciones] = useState(0);
  const [cursosReprobados, setCursosReprobados] = useState(0);
  const [actividadesExtracurriculares, setActividadesExtracurriculares] = useState("");
  const [reportesDisciplinarios, setReportesDisciplinarios] = useState(0);

  // UI state
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  // Resultado
  const [resultado, setResultado] = useState(null); // { prediccion, prob_riesgo }

  const validarCampos = () => {
    // Reglas básicas
    if (isNaN(promedioActual) || promedioActual < 0 || promedioActual > 100) return "Promedio actual debe estar entre 0 y 100";
    if (isNaN(asistenciaClases) || asistenciaClases < 0 || asistenciaClases > 100) return "Asistencia debe estar entre 0 y 100";
    if (isNaN(tareasEntregadas) || tareasEntregadas < 0 || tareasEntregadas > 100) return "Tareas entregadas debe estar entre 0 y 100";
    if (isNaN(participacionClase) || participacionClase < 0 || participacionClase > 100) return "Participación debe estar entre 0 y 100";
    if (isNaN(horasEstudio) || horasEstudio < 0) return "Horas de estudio no puede ser negativa";
    if (isNaN(promedioEvaluaciones) || promedioEvaluaciones < 0 || promedioEvaluaciones > 100) return "Promedio evaluaciones debe estar entre 0 y 100";
    if (isNaN(cursosReprobados) || cursosReprobados < 0) return "Cursos reprobados no puede ser negativo";
    if (isNaN(reportesDisciplinarios) || reportesDisciplinarios < 0) return "Reportes disciplinarios no puede ser negativo";
    return null;
  };

  const handlePredecir = async (e) => {
    e.preventDefault();
    setError(null);
    setResultado(null);

    const errorMsg = validarCampos();
    if (errorMsg) {
      setError(errorMsg);
      return;
    }

    // Construir lista de actividades desde la cadena separada por comas
    const actividades = actividadesExtracurriculares
      .split(",")
      .map((a) => a.trim())
      .filter((a) => a.length > 0);

    const payload = {
      promedio_actual: Number(promedioActual),
      asistencia_clases: Number(asistenciaClases),
      tareas_entregadas: Number(tareasEntregadas),
      participacion_clase: Number(participacionClase),
      horas_estudio: Number(horasEstudio),
      promedio_evaluaciones: Number(promedioEvaluaciones),
      cursos_reprobados: Number(cursosReprobados),
      actividades_extracurriculares: actividades,
      reportes_disciplinarios: Number(reportesDisciplinarios),
    };

    try {
      setCargando(true);
      if (typeof Service.predict !== "function") {
        setError("Predicción no disponible por el momento");
        return;
      }
      const resp = await Service.predict(payload);
      setResultado({ prediccion: resp.prediccion, prob_riesgo: resp.prob_riesgo });
    } catch (err) {
      const msg = err?.error || err?.message || "Error al predecir";
      setError(msg);
    } finally {
      setCargando(false);
    }
  };

  const handleCancelar = () => {
    setPromedioActual(0);
    setAsistenciaClases(0);
    setTareasEntregadas(0);
    setParticipacionClase(0);
    setHorasEstudio(0);
    setPromedioEvaluaciones(0);
    setCursosReprobados(0);
    setActividadesExtracurriculares("");
    setReportesDisciplinarios(0);
    setResultado(null);
    setError(null);
  };

  return (
    <div className="w-full px-2 md:px-6 py-6">
      <div className="mb-6">
        <h1 className="text-2xl md:text-3xl font-semibold text-white">Predicción de Riesgo</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Columna izquierda: Formulario */}
        <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5">
          <form onSubmit={handlePredecir} className="space-y-4">
            {error && (
              <div className="rounded-md border border-red-600 bg-red-900/30 text-red-200 px-3 py-2 text-sm">
                {error}
              </div>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-slate-300 text-sm">Promedio actual</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="Ej: 75.5"
                  value={promedioActual}
                  onChange={(e) => setPromedioActual(parseFloat(e.target.value) || 0)}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                />
                <p className="text-xs text-slate-400 mt-1">Rango permitido: 0 a 100</p>
              </div>
              <div>
                <label className="text-slate-300 text-sm">Asistencia a clases (%)</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="Ej: 90"
                  value={asistenciaClases}
                  onChange={(e) => setAsistenciaClases(parseFloat(e.target.value) || 0)}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                />
                <p className="text-xs text-slate-400 mt-1">Rango permitido: 0 a 100</p>
              </div>

              <div>
                <label className="text-slate-300 text-sm">Tareas entregadas (%)</label>
                <input
                  type="number"
                  step="1"
                  placeholder="Ej: 80"
                  value={tareasEntregadas}
                  onChange={(e) => setTareasEntregadas(parseInt(e.target.value) || 0)}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                />
                <p className="text-xs text-slate-400 mt-1">Rango permitido: 0 a 100</p>
              </div>
              <div>
                <label className="text-slate-300 text-sm">Participación en clase (%)</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="Ej: 70"
                  value={participacionClase}
                  onChange={(e) => setParticipacionClase(parseFloat(e.target.value) || 0)}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                />
                <p className="text-xs text-slate-400 mt-1">Rango permitido: 0 a 100</p>
              </div>

              <div>
                <label className="text-slate-300 text-sm">Horas de estudio</label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="Ej: 12.5"
                  value={horasEstudio}
                  onChange={(e) => setHorasEstudio(parseFloat(e.target.value) || 0)}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                />
                <p className="text-xs text-slate-400 mt-1">Mínimo: 0 (no negativo)</p>
              </div>
              <div>
                <label className="text-slate-300 text-sm">Promedio evaluaciones</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="Ej: 68.2"
                  value={promedioEvaluaciones}
                  onChange={(e) => setPromedioEvaluaciones(parseFloat(e.target.value) || 0)}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                />
                <p className="text-xs text-slate-400 mt-1">Rango permitido: 0 a 100</p>
              </div>

              <div>
                <label className="text-slate-300 text-sm">Cursos reprobados</label>
                <input
                  type="number"
                  step="1"
                  placeholder="Ej: 1"
                  value={cursosReprobados}
                  onChange={(e) => setCursosReprobados(parseInt(e.target.value) || 0)}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                />
                <p className="text-xs text-slate-400 mt-1">Mínimo: 0 (no negativo)</p>
              </div>
              <div>
                <label className="text-slate-300 text-sm">Reportes disciplinarios</label>
                <input
                  type="number"
                  step="1"
                  placeholder="Ej: 0"
                  value={reportesDisciplinarios}
                  onChange={(e) => setReportesDisciplinarios(parseInt(e.target.value) || 0)}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                />
                <p className="text-xs text-slate-400 mt-1">Mínimo: 0 (no negativo)</p>
              </div>
            </div>

            <div>
              <label className="text-slate-300 text-sm">Actividades extracurriculares (lista separada por comas)</label>
              <input
                type="text"
                placeholder="Ej: football, musica, voluntariado"
                value={actividadesExtracurriculares}
                onChange={(e) => setActividadesExtracurriculares(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
              />
              <p className="text-xs text-slate-400 mt-1">Ejemplos: futbol, musica, arte, voluntariado (separados por comas)</p>
            </div>

            <div className="flex flex-wrap gap-3 pt-2">
              <button
                type="submit"
                disabled={cargando}
                className="inline-flex items-center rounded-md bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {cargando ? "Prediciendo..." : "Predecir"}
              </button>
              <button
                type="button"
                onClick={handleCancelar}
                className="inline-flex items-center rounded-md bg-slate-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-600"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>

        {/* Columna derecha: Resultado */}
        <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5 flex items-center justify-center">
          <div className="text-center">
            <div className="text-slate-100 text-xl font-semibold mb-2">Resultado</div>
            <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-6 min-w-[280px] min-h-[160px] flex flex-col gap-3 items-center justify-center">
              {resultado == null ? (
                <span className="text-slate-300">Aún no hay predicción</span>
              ) : (
                <div className="w-full max-w-xs">
                  <div
                    className={`text-sm font-medium mb-2 ${resultado.prediccion === 1 ? "text-red-300" : "text-emerald-300"}`}
                  >
                    {resultado.prediccion === 1 ? "Alto riesgo" : "Bajo riesgo"}
                    <span className="ml-2 inline-flex align-middle" aria-hidden="true">
                      {Math.round((resultado.prob_riesgo || 0) * 100) > 51 ? (
                        // Icono pulgar abajo (misma imagen, rotada 180°)
                        <img
                          src="https://img.icons8.com/ios/50/facebook-like--v1.png"
                          width="70"
                          height="70"
                          alt="facebook-dislike"
                          style={{ transform: "rotate(180deg)", filter: "invert(1) brightness(200%)" }}
                        />
                      ) : (
                        // Icono pulgar arriba (imagen externa solicitada)
                        <img
                          src="https://img.icons8.com/ios/50/facebook-like--v1.png"
                          width="70"
                          height="70"
                          alt="facebook-like"
                          style={{ filter: "invert(1) brightness(200%)" }}
                        />
                      )}
                    </span>
                  </div>
                  <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${resultado.prediccion === 1 ? "bg-red-500" : "bg-emerald-500"}`}
                      style={{ width: `${Math.round((resultado.prob_riesgo || 0) * 100)}%` }}
                    />
                  </div>
                  <div className="text-slate-300 text-xs mt-1 text-right">
                    Prob. riesgo: {Math.round((resultado.prob_riesgo || 0) * 100)}%
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
