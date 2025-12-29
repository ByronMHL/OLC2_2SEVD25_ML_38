import { useEffect, useState } from "react";
import Service from "../../service/Service.js";

export default function Entrenamiento() {
  // Selección de algoritmo
  const [algorithm, setAlgorithm] = useState("kmeans"); // 'kmeans' | 'hierarchical' | 'auto_k'

  // Parámetros KMeans
  const [kmNClusters, setKmNClusters] = useState(3);
  const [kmInit, setKmInit] = useState("k-means++"); // 'k-means++' | 'random'
  const [kmNInit, setKmNInit] = useState(10);
  const [kmMaxIter, setKmMaxIter] = useState(300);
  const [kmRandomState, setKmRandomState] = useState(42);

  // Parámetros Hierarchical
  const [hiNClusters, setHiNClusters] = useState(3);
  const [hiLinkage, setHiLinkage] = useState("ward"); // 'ward' | 'complete' | 'average' | 'single'

  // Estado UI
  const [isSaving, setIsSaving] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [alert, setAlert] = useState(null);
  const [result, setResult] = useState(null);
  const [modelsStatus, setModelsStatus] = useState(null);

  // Parámetros Text KMeans + TF-IDF
  const [tkNClusters, setTkNClusters] = useState(6);
  const [tkInit, setTkInit] = useState("k-means++");
  const [tkNInit, setTkNInit] = useState(10);
  const [tkMaxIter, setTkMaxIter] = useState(500);
  const [tkRandomState, setTkRandomState] = useState(42);
  const [tfidfMaxFeatures, setTfidfMaxFeatures] = useState(5000);
  const [tfidfMinDf, setTfidfMinDf] = useState(1);
  const [tfidfMaxDf, setTfidfMaxDf] = useState(1.0);

  // Cargar parámetros actuales del backend al montar
  useEffect(() => {
    const fetchParams = async () => {
      try {
        const all = await Service.getAllHyperparams();
        if (all?.kmeans) {
          const p = all.kmeans;
          if (p.n_clusters != null) setKmNClusters(Number(p.n_clusters));
          if (p.init) setKmInit(p.init);
          if (p.n_init != null) setKmNInit(Number(p.n_init));
          if (p.max_iter != null) setKmMaxIter(Number(p.max_iter));
          if (p.random_state != null) setKmRandomState(Number(p.random_state));
        }
        if (all?.hierarchical) {
          const p = all.hierarchical;
          if (p.n_clusters != null) setHiNClusters(Number(p.n_clusters));
          if (p.linkage) setHiLinkage(p.linkage);
        }
        if (all?.text_kmeans) {
          const p = all.text_kmeans;
          if (p.n_clusters != null) setTkNClusters(Number(p.n_clusters));
          if (p.init) setTkInit(p.init);
          if (p.n_init != null) setTkNInit(Number(p.n_init));
          if (p.max_iter != null) setTkMaxIter(Number(p.max_iter));
          if (p.random_state != null) setTkRandomState(Number(p.random_state));
          if (p.tfidf_max_features != null) setTfidfMaxFeatures(Number(p.tfidf_max_features));
          if (p.tfidf_min_df != null) setTfidfMinDf(p.tfidf_min_df);
          if (p.tfidf_max_df != null) setTfidfMaxDf(Number(p.tfidf_max_df));
        }
      } catch (e) {
        // Silencioso; se puede mostrar en UI si se desea
      }
    };
    fetchParams();
  }, []);

  const saveConfig = async () => {
    setAlert(null);
    setIsSaving(true);
    try {
      if (algorithm === "kmeans") {
        await Service.setKMeansParams({
          n_clusters: kmNClusters,
          init: kmInit,
          n_init: kmNInit,
          max_iter: kmMaxIter,
          random_state: kmRandomState,
        });
      } else if (algorithm === "hierarchical") {
        await Service.setHierarchicalParams({
          n_clusters: hiNClusters,
          linkage: hiLinkage,
        });
      } else if (algorithm === "text_kmeans") {
        await Service.setTextKMeansParams({
          n_clusters: tkNClusters,
          init: tkInit,
          n_init: tkNInit,
          max_iter: tkMaxIter,
          random_state: tkRandomState,
          tfidf_max_features: tfidfMaxFeatures,
          tfidf_min_df: tfidfMinDf,
          tfidf_max_df: tfidfMaxDf,
        });
      }
      setAlert({ type: "success", message: "Configuración guardada correctamente" });
    } catch (err) {
      const msg = typeof err === "string" ? err : err?.error || "No se pudo guardar la configuración";
      setAlert({ type: "error", message: msg });
    } finally {
      setIsSaving(false);
    }
  };

  const runTraining = async () => {
    setAlert(null);
    setIsTraining(true);
    setResult(null);
    try {
      let res;
      if (algorithm === "kmeans") {
        res = await Service.trainKMeans();
      } else if (algorithm === "hierarchical") {
        res = await Service.trainHierarchical();
      } else if (algorithm === "auto_k") {
        res = await Service.trainAutoK();
      } else if (algorithm === "text_kmeans") {
        res = await Service.trainTextKMeans();
      }
      setResult(res || null);
      setAlert({ type: "success", message: res?.message || "Entrenamiento completado" });
      const status = await Service.getModelsStatus();
      setModelsStatus(status);
    } catch (err) {
      const msg = typeof err === "string" ? err : err?.error || "Error al entrenar";
      setAlert({ type: "error", message: msg });
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="w-full px-2 md:px-6 py-6">
      <div className="mb-6 text-center">
        <h1 className="text-2xl md:text-3xl font-semibold text-white">Entrenamiento (Aprendizaje No Supervisado)</h1>
        <p className="mt-2 text-slate-400 text-sm">Configura y ejecuta K-Means o Clustering Jerárquico. Opcionalmente, usa Auto-K para elegir el número óptimo de clusters.</p>
      </div>

      {alert && (
        <div className={alert.type === "success" ? "mb-4 rounded-lg border border-green-200 bg-green-50 text-green-800 px-4 py-3" : "mb-4 rounded-lg border border-red-200 bg-red-50 text-red-800 px-4 py-3"}>
          {alert.message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuración */}
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5">
            <div className="text-slate-100 font-semibold mb-3">Algoritmo</div>
            <div className="flex flex-wrap gap-2">
              <button
                className={`px-4 py-2 rounded-md border ${algorithm === 'kmeans' ? 'bg-amber-600 border-amber-600 text-white' : 'bg-slate-800 border-slate-700 text-slate-200'}`}
                onClick={() => setAlgorithm('kmeans')}
              >K-Means</button>
              <button
                className={`px-4 py-2 rounded-md border ${algorithm === 'hierarchical' ? 'bg-amber-600 border-amber-600 text-white' : 'bg-slate-800 border-slate-700 text-slate-200'}`}
                onClick={() => setAlgorithm('hierarchical')}
              >Clustering Jerárquico</button>
              <button
                className={`px-4 py-2 rounded-md border ${algorithm === 'auto_k' ? 'bg-amber-600 border-amber-600 text-white' : 'bg-slate-800 border-slate-700 text-slate-200'}`}
                onClick={() => setAlgorithm('auto_k')}
              >Auto-K (K-Means)</button>
              <button
                className={`px-4 py-2 rounded-md border ${algorithm === 'text_kmeans' ? 'bg-amber-600 border-amber-600 text-white' : 'bg-slate-800 border-slate-700 text-slate-200'}`}
                onClick={() => setAlgorithm('text_kmeans')}
              >Texto (TF-IDF + KMeans)</button>
            </div>
          </div>

          {/* Parámetros por algoritmo */}
          {algorithm === 'kmeans' && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5">
              <div className="text-slate-100 font-semibold mb-2">Parámetros K-Means</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-300 text-sm">n_clusters</label>
                  <input type="number" min={2} value={kmNClusters} onChange={(e) => setKmNClusters(Math.max(2, parseInt(e.target.value) || 2))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
                <div>
                  <label className="text-slate-300 text-sm">init</label>
                  <select value={kmInit} onChange={(e) => setKmInit(e.target.value)} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100">
                    <option value="k-means++">k-means++ (recomendado)</option>
                    <option value="random">random</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-300 text-sm">n_init</label>
                  <input type="number" min={1} value={kmNInit} onChange={(e) => setKmNInit(Math.max(1, parseInt(e.target.value) || 1))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
                <div>
                  <label className="text-slate-300 text-sm">max_iter</label>
                  <input type="number" min={1} value={kmMaxIter} onChange={(e) => setKmMaxIter(Math.max(1, parseInt(e.target.value) || 1))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
                <div>
                  <label className="text-slate-300 text-sm">random_state</label>
                  <input type="number" min={0} value={kmRandomState} onChange={(e) => setKmRandomState(Math.max(0, parseInt(e.target.value) || 0))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
              </div>
              <p className="mt-2 text-xs text-slate-400">Coincide con parámetros aceptados por el backend en /hyperparameters/kmeans.</p>
              <div className="mt-3">
                <button onClick={saveConfig} disabled={isSaving} className="inline-flex items-center rounded-md bg-amber-600 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-700 disabled:opacity-60">{isSaving ? 'Guardando...' : 'Guardar configuración'}</button>
              </div>
            </div>
          )}

          {algorithm === 'hierarchical' && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5">
              <div className="text-slate-100 font-semibold mb-2">Parámetros Clustering Jerárquico</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-300 text-sm">n_clusters</label>
                  <input type="number" min={2} value={hiNClusters} onChange={(e) => setHiNClusters(Math.max(2, parseInt(e.target.value) || 2))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
                <div>
                  <label className="text-slate-300 text-sm">linkage</label>
                  <select value={hiLinkage} onChange={(e) => setHiLinkage(e.target.value)} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100">
                    <option value="ward">ward (recomendado)</option>
                    <option value="complete">complete</option>
                    <option value="average">average</option>
                    <option value="single">single</option>
                  </select>
                </div>
              </div>
              <p className="mt-2 text-xs text-slate-400">Coincide con parámetros aceptados por el backend en /hyperparameters/hierarchical.</p>
              <div className="mt-3">
                <button onClick={saveConfig} disabled={isSaving} className="inline-flex items-center rounded-md bg-amber-600 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-700 disabled:opacity-60">{isSaving ? 'Guardando...' : 'Guardar configuración'}</button>
              </div>
            </div>
          )}

          {algorithm === 'auto_k' && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5">
              <div className="text-slate-100 font-semibold mb-2">Auto-K (K-Means)</div>
              <p className="text-slate-300 text-sm">Determina automáticamente el número de clusters usando la métrica de silhouette y entrena K-Means con ese valor. No requiere configuración adicional.</p>
            </div>
          )}

          {algorithm === 'text_kmeans' && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5">
              <div className="text-slate-100 font-semibold mb-2">Parámetros Texto (TF-IDF + KMeans)</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-300 text-sm">tfidf_max_features</label>
                  <input type="number" min={100} value={tfidfMaxFeatures} onChange={(e) => setTfidfMaxFeatures(Math.max(100, parseInt(e.target.value) || 100))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
                <div>
                  <label className="text-slate-300 text-sm">tfidf_min_df</label>
                  <input type="text" value={tfidfMinDf} onChange={(e) => {
                    const v = e.target.value;
                    // Permitir números enteros >=1 o decimales 0..1
                    if (v === "") { setTfidfMinDf(1); return; }
                    const asNum = Number(v);
                    if (!isNaN(asNum)) setTfidfMinDf(asNum);
                  }} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                  <p className="mt-1 text-xs text-slate-500">Entero (≥1) o proporción [0,1].</p>
                </div>
                <div>
                  <label className="text-slate-300 text-sm">tfidf_max_df</label>
                  <input type="number" step="0.01" min={0.01} max={1} value={tfidfMaxDf} onChange={(e) => setTfidfMaxDf(Math.min(1, Math.max(0.01, parseFloat(e.target.value) || 1)))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
                <div>
                  <label className="text-slate-300 text-sm">n_clusters</label>
                  <input type="number" min={2} value={tkNClusters} onChange={(e) => setTkNClusters(Math.max(2, parseInt(e.target.value) || 2))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
                <div>
                  <label className="text-slate-300 text-sm">init</label>
                  <select value={tkInit} onChange={(e) => setTkInit(e.target.value)} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100">
                    <option value="k-means++">k-means++ (recomendado)</option>
                    <option value="random">random</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-300 text-sm">n_init</label>
                  <input type="number" min={1} value={tkNInit} onChange={(e) => setTkNInit(Math.max(1, parseInt(e.target.value) || 1))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
                <div>
                  <label className="text-slate-300 text-sm">max_iter</label>
                  <input type="number" min={1} value={tkMaxIter} onChange={(e) => setTkMaxIter(Math.max(1, parseInt(e.target.value) || 1))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
                <div>
                  <label className="text-slate-300 text-sm">random_state</label>
                  <input type="number" min={0} value={tkRandomState} onChange={(e) => setTkRandomState(Math.max(0, parseInt(e.target.value) || 0))} className="mt-1 w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-slate-100" />
                </div>
              </div>
              <p className="mt-2 text-xs text-slate-400">Parámetros para TF-IDF y KMeans textual. Coinciden con /hyperparameters/text_kmeans.</p>
              <div className="mt-3">
                <button onClick={saveConfig} disabled={isSaving} className="inline-flex items-center rounded-md bg-amber-600 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-700 disabled:opacity-60">{isSaving ? 'Guardando...' : 'Guardar configuración'}</button>
              </div>
            </div>
          )}
        </div>

        {/* Ejecución y resultados */}
        <div className="flex flex-col items-stretch lg:items-center justify-start gap-4">
          <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5 w-full">
            <div className="text-slate-100 font-semibold mb-2">Entrenamiento</div>
            <p className="text-slate-300 text-sm mb-3">Asegúrate de haber cargado y limpiado los datos antes de entrenar.</p>
            <button onClick={runTraining} disabled={isTraining} className="inline-flex items-center rounded-xl bg-amber-600 px-6 py-3 text-base font-semibold text-white hover:bg-amber-700 disabled:opacity-60 shadow-md">
              {isTraining ? 'Entrenando...' : (algorithm === 'auto_k' ? 'Ejecutar Auto-K (K-Means)' : 'Ejecutar Entrenamiento')}
            </button>
          </div>

          {result && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5 w-full">
              <div className="text-slate-100 font-semibold mb-2">Resultados</div>
              <div className="text-slate-300 text-sm">
                {result.model_info && (
                  <div className="mb-2">
                    <div>Algoritmo: <span className="font-semibold text-slate-100">{result.model_info.algorithm}</span></div>
                    <div>Clusters: <span className="font-semibold text-slate-100">{result.model_info.n_clusters}</span></div>
                    <div>Muestras: <span className="font-semibold text-slate-100">{result.model_info.n_samples}</span></div>
                    <div>Características: <span className="font-semibold text-slate-100">{result.model_info.n_features}</span></div>
                    {result.model_info.linkage && (<div>Linkage: <span className="font-semibold text-slate-100">{result.model_info.linkage}</span></div>)}
                  </div>
                )}
                {result.metrics && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {Object.entries(result.metrics).map(([k,v]) => (
                      <div key={k} className="flex justify-between"><span className="text-slate-400">{k}</span><span className="text-slate-100 font-mono">{typeof v === 'number' ? v.toFixed(4) : v}</span></div>
                    ))}
                  </div>
                )}
                {result.cluster_distribution && (
                  <div className="mt-3">
                    <div className="text-slate-100 font-semibold mb-1">Distribución de clusters</div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {Object.entries(result.cluster_distribution).map(([k,v]) => (
                        <div key={k} className="rounded-md bg-slate-800 border border-slate-700 px-3 py-2 flex items-center justify-between">
                          <span className="text-slate-300">Cluster {k}</span>
                          <span className="text-slate-100 font-mono">{v}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {modelsStatus && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/50 shadow-md p-5 w-full">
              <div className="text-slate-100 font-semibold mb-2">Estado de Modelos</div>
              <div className="text-slate-300 text-sm grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div className="rounded-md bg-slate-800 border border-slate-700 px-3 py-2">
                  <div className="text-slate-100 font-semibold">K-Means</div>
                  <div>Entrenado: {modelsStatus.kmeans?.trained ? 'Sí' : 'No'}</div>
                  <div>Clusters: {modelsStatus.kmeans?.n_clusters ?? '-'}</div>
                  <div>Etiquetas: {modelsStatus.kmeans?.labels_count ?? 0}</div>
                </div>
                <div className="rounded-md bg-slate-800 border border-slate-700 px-3 py-2">
                  <div className="text-slate-100 font-semibold">Jerárquico</div>
                  <div>Entrenado: {modelsStatus.hierarchical?.trained ? 'Sí' : 'No'}</div>
                  <div>Clusters: {modelsStatus.hierarchical?.n_clusters ?? '-'}</div>
                  <div>Etiquetas: {modelsStatus.hierarchical?.labels_count ?? 0}</div>
                </div>
                <div className="rounded-md bg-slate-800 border border-slate-700 px-3 py-2">
                  <div className="text-slate-100 font-semibold">Texto (TF-IDF + KMeans)</div>
                  <div>Entrenado: {modelsStatus.text_kmeans?.trained ? 'Sí' : 'No'}</div>
                  <div>Clusters: {modelsStatus.text_kmeans?.n_clusters ?? '-'}</div>
                  <div>Etiquetas: {modelsStatus.text_kmeans?.labels_count ?? 0}</div>
                </div>
                <div className="rounded-md bg-slate-800 border border-slate-700 px-3 py-2">
                  <div className="text-slate-100 font-semibold">K Óptimo</div>
                  <div>Valor: {modelsStatus.optimal_k ?? '-'}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
