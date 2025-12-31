import React, { useEffect, useMemo, useRef, useState } from "react";
import { getNumericProfile, getTextPatterns, getDescriptions, exportReports } from "../../service/Conexion/ComunicacionBack";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

// Utilidad para descargar CSV
function downloadCSV(name, rows) {
  const csvContent = rows.map(r => r.map(v => `"${String(v).replaceAll('"', '""')}"`).join(",")).join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

export default function Reportes() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [clusterCol, setClusterCol] = useState("kmeans_cluster");
  const [topN, setTopN] = useState(12);
  const [zHigh, setZHigh] = useState(0.7);
  const [zLow, setZLow] = useState(-0.7);

  const [numeric, setNumeric] = useState(null);
  const [patterns, setPatterns] = useState(null);
  const [descriptions, setDescriptions] = useState(null);
  const [exportInfo, setExportInfo] = useState(null);
  const [sentiment, setSentiment] = useState(null);

  const previewRef = useRef(null);

  const buildFileUrl = (p, extra = "") => `http://localhost:5000/api/reports/file?path=${encodeURIComponent(p)}&cb=${Date.now()}${extra ? `-${extra}` : ""}`;

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [n, p, d, s] = await Promise.all([
        getNumericProfile(clusterCol),
        getTextPatterns(topN),
        getDescriptions(clusterCol, topN, zHigh, zLow),
        // Fetch directo del endpoint de sentimientos
        fetch("http://localhost:5000/api/reports/sentiment").then(r => r.json()),
      ]);
      if (!n.success || !p.success || !d.success || !s.success) {
        throw new Error("Error en uno de los endpoints de reportes");
      }
      setNumeric(n.data);
      setPatterns(p.data);
      setDescriptions(d.data);
      setSentiment(s.data);
    } catch (e) {
      setError(e?.error || e?.message || "Error al obtener reportes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const clusters = useMemo(() => {
    const keys = numeric?.profiles ? Object.keys(numeric.profiles) : [];
    return keys;
  }, [numeric]);

  const onDownloadCSV = () => {
    if (!numeric || !patterns || !descriptions) return;
    const rows = [];
    rows.push(["Cluster", "Size", "Descripcion", "TopTerms"]);
    clusters.forEach(cl => {
      const size = numeric.profiles[cl]?.size ?? 0;
      const desc = descriptions.clusters[cl]?.text ?? "";
      const terms = (patterns.clusters[cl]?.top_terms || []).map(t => t.term).join("|");
      rows.push([cl, size, desc, terms]);
    });
    downloadCSV("reportes_segmentos.csv", rows);
  };

  const onDownloadPDF = async () => {
    try {
      setLoading(true);
      const element = previewRef.current;
      const canvas = await html2canvas(element, {
        backgroundColor: "#0b1220",
        scale: 2,
        useCORS: true,
        allowTaint: true,
        imageTimeout: 15000,
        logging: false,
        onclone: (doc) => {
          const el = doc.getElementById("report-preview");
          if (!el) return;
          const style = doc.createElement("style");
          style.innerHTML = `
            #report-preview, #report-preview * {
              background-color: transparent !important;
              color: #e2e8f0 !important;
              border-color: #334155 !important;
            }
            #report-preview .bg-slate-900 { background-color: #0b1220 !important; }
            #report-preview .bg-slate-800 { background-color: #111827 !important; }
            #report-preview .bg-slate-700 { background-color: #1f2937 !important; }
            #report-preview .bg-indigo-500 { background-color: #6366f1 !important; }
            #report-preview .bg-emerald-500 { background-color: #10b981 !important; }
            #report-preview .bg-white { background-color: #e5e7eb !important; }
            #report-preview .text-slate-400 { color: #94a3b8 !important; }
            #report-preview .text-slate-300 { color: #cbd5e1 !important; }
          `;
          doc.head.appendChild(style);
        },
      });
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF({ orientation: "portrait", unit: "pt", format: "a4" });
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = pageWidth - 40; // margins
      const imgHeight = canvas.height * (imgWidth / canvas.width);
      let y = 20;
      if (imgHeight < pageHeight - 40) {
        pdf.addImage(imgData, "PNG", 20, y, imgWidth, imgHeight);
      } else {
        // Split into multiple pages
        let position = 0;
        while (position < imgHeight) {
          pdf.addImage(imgData, "PNG", 20, y - position, imgWidth, imgHeight);
          position += pageHeight - 40;
          if (position < imgHeight) pdf.addPage();
        }
      }
      pdf.save("reportes_segmentos.pdf");
    } catch (e) {
      setError(e?.message || "Error al generar PDF");
    } finally {
      setLoading(false);
    }
  };

  const onExportBackend = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await exportReports(clusterCol, topN, zHigh, zLow);
      if (!res.success) throw new Error(res.error || "Error en exportación");
      setExportInfo(res.data);
    } catch (e) {
      setError(e?.error || e?.message || "Error al exportar reportes en backend");
    } finally {
      setLoading(false);
    }
  };

  const normalizeByFeature = (feature) => {
    if (!numeric) return (v) => 0;
    const means = clusters.map(cl => numeric.profiles[cl]?.mean?.[feature] ?? 0);
    const max = Math.max(...means);
    const min = Math.min(...means);
    return (v) => max === min ? 0 : ((v - min) / (max - min)) * 100;
  };

  return (
    <div className="p-6 text-slate-100">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Reportes de Segmentación</h2>
        <div className="flex gap-2">
          <button onClick={onDownloadCSV} className="px-3 py-2 bg-slate-700 rounded hover:bg-slate-600">Descargar CSV</button>
          <button onClick={onDownloadPDF} className="px-3 py-2 bg-slate-700 rounded hover:bg-slate-600">Descargar PDF</button>
        </div>
      </div>

      {/* Controles */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-slate-900 p-4 rounded border border-slate-800 mb-4">
        <div>
          <label className="text-sm text-slate-400">Columna de cluster</label>
          <select value={clusterCol} onChange={(e) => setClusterCol(e.target.value)} className="mt-1 w-full bg-slate-800 border border-slate-700 rounded p-2">
            <option value="kmeans_cluster">kmeans_cluster</option>
            <option value="hierarchical_cluster">hierarchical_cluster</option>
          </select>
        </div>
        <div>
          <label className="text-sm text-slate-400">Top N términos</label>
          <input type="number" min={3} max={30} value={topN} onChange={(e) => setTopN(Number(e.target.value))} className="mt-1 w-full bg-slate-800 border border-slate-700 rounded p-2" />
        </div>
        <div>
          <label className="text-sm text-slate-400">Z-Score alto (z_high)</label>
          <input type="number" step="0.1" value={zHigh} onChange={(e) => setZHigh(Number(e.target.value))} className="mt-1 w-full bg-slate-800 border border-slate-700 rounded p-2" />
        </div>
        <div>
          <label className="text-sm text-slate-400">Z-Score bajo (z_low)</label>
          <input type="number" step="0.1" value={zLow} onChange={(e) => setZLow(Number(e.target.value))} className="mt-1 w-full bg-slate-800 border border-slate-700 rounded p-2" />
        </div>
        <div className="md:col-span-4">
          <button onClick={fetchAll} className="px-3 py-2 bg-indigo-600 rounded hover:bg-indigo-500">Actualizar</button>
        </div>
      </div>

      {loading && <div className="text-slate-300">Cargando...</div>}
      {error && <div className="text-red-400">{String(error)}</div>}

      {/* Preview container for PDF */}
      <div id="report-preview" ref={previewRef} className="space-y-6">
        {/* Descripciones */}
        <section className="bg-slate-900 p-4 rounded border border-slate-800">
          <h3 className="text-lg font-medium mb-2">Descripciones por segmento</h3>
          <div className="space-y-2">
            {descriptions && clusters.map(cl => (
              <div key={cl} className="p-3 bg-slate-800 rounded">
                <div className="flex items-center justify-between">
                  <span className="font-semibold">Segmento {cl}</span>
                  <span className="text-sm text-slate-400">n={numeric?.profiles?.[cl]?.size ?? 0}</span>
                </div>
                <p className="text-sm mt-1 text-slate-300">{descriptions?.clusters?.[cl]?.text}</p>
              </div>
            ))}
            {!descriptions && <p className="text-slate-400 text-sm">Sin descripciones disponibles.</p>}
          </div>
        </section>

        {/* Tablas resumen */}
        <section className="bg-slate-900 p-4 rounded border border-slate-800">
          <h3 className="text-lg font-medium mb-2">Tabla resumen (medias)</h3>
          {numeric ? (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr>
                    <th className="text-left p-2">Cluster</th>
                    {numeric.num_features.map(f => (
                      <th key={f} className="text-left p-2">{f}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {clusters.map(cl => (
                    <tr key={cl} className="border-t border-slate-800">
                      <td className="p-2">{cl}</td>
                      {numeric.num_features.map(f => (
                        <td key={f} className="p-2 text-slate-300">{Number(numeric.profiles[cl]?.mean?.[f] ?? 0).toFixed(2)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Sin datos numéricos.</p>
          )}
        </section>

        {/* Barras por feature */}
        <section className="bg-slate-900 p-4 rounded border border-slate-800">
          <h3 className="text-lg font-medium mb-2">Barras (media normalizada)</h3>
          {numeric ? (
            <div className="space-y-4">
              {numeric.num_features.map(f => {
                const norm = normalizeByFeature(f);
                return (
                  <div key={f}>
                    <div className="text-sm text-slate-400 mb-1">{f}</div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                      {clusters.map(cl => {
                        const val = numeric.profiles[cl]?.mean?.[f] ?? 0;
                        const w = norm(val);
                        return (
                          <div key={cl} className="bg-slate-800 rounded p-2">
                            <div className="text-xs text-slate-400">Cluster {cl}</div>
                            <div className="h-2 bg-slate-700 rounded">
                              <div style={{ width: `${w}%` }} className="h-2 bg-indigo-500 rounded" />
                            </div>
                            <div className="text-xs text-slate-400 mt-1">{Number(val).toFixed(2)}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Sin datos numéricos.</p>
          )}
        </section>

        {/* Boxplots simples usando p25/p75/median */}
        <section className="bg-slate-900 p-4 rounded border border-slate-800">
          <h3 className="text-lg font-medium mb-2">Boxplots (p25/median/p75)</h3>
          {numeric ? (
            <div className="space-y-4">
              {numeric.num_features.map(f => (
                <div key={f}>
                  <div className="text-sm text-slate-400 mb-1">{f}</div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    {clusters.map(cl => {
                      const p25 = numeric.profiles[cl]?.p25?.[f] ?? 0;
                      const med = numeric.profiles[cl]?.median?.[f] ?? 0;
                      const p75 = numeric.profiles[cl]?.p75?.[f] ?? 0;
                      const min = Math.min(p25, med, p75);
                      const max = Math.max(p25, med, p75);
                      const scale = (v) => max === min ? 50 : ((v - min) / (max - min)) * 100;
                      return (
                        <div key={cl} className="bg-slate-800 rounded p-2">
                          <div className="text-xs text-slate-400">Cluster {cl}</div>
                          <div className="h-2 bg-slate-700 rounded relative">
                            <div style={{ left: `${scale(p25)}%`, width: `${Math.max(scale(p75) - scale(p25), 2)}%` }} className="absolute top-0 h-2 bg-emerald-500 rounded" />
                            <div style={{ left: `${scale(med)}%` }} className="absolute -top-1 w-1 h-4 bg-white rounded" />
                          </div>
                          <div className="text-xs text-slate-400 mt-1">p25 {Number(p25).toFixed(2)} | median {Number(med).toFixed(2)} | p75 {Number(p75).toFixed(2)}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Sin datos numéricos.</p>
          )}
        </section>

        {/* Patrones textuales */}
        <section className="bg-slate-900 p-4 rounded border border-slate-800">
          <h3 className="text-lg font-medium mb-2">Patrones textuales (Top términos)</h3>
          {patterns ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              {clusters.map(cl => (
                <div key={cl} className="bg-slate-800 rounded p-3">
                  <div className="text-xs text-slate-400">Cluster {cl}</div>
                  <ul className="mt-1 space-y-1 text-sm">
                    {(patterns.clusters[cl]?.top_terms || []).map((t, idx) => (
                      <li key={idx} className="flex justify-between"><span>{t.term}</span><span className="text-slate-400">{Number(t.weight).toFixed(3)}</span></li>
                    ))}
                  </ul>
                  {/* Figura de términos por cluster, si existe */}
                  {patterns.clusters[cl]?.figure ? (
                    <div className="mt-2">
                      <img
                        alt={`Top términos Cluster ${cl}`}
                        className="rounded border border-slate-700"
                        crossOrigin="anonymous"
                        src={buildFileUrl(patterns.clusters[cl].figure, `p-${cl}`)}
                        onError={(e) => { e.currentTarget.src = buildFileUrl(patterns.clusters[cl].figure, `p-${cl}-retry`); }}
                      />
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Sin patrones textuales.</p>
          )}
        </section>

        {/* Sentimientos (independiente del clustering) */}
        <section className="bg-slate-900 p-4 rounded border border-slate-800">
          <h3 className="text-lg font-medium mb-2">Análisis de Sentimientos</h3>
          {sentiment ? (
            <div className="space-y-4">
              {/* Resumen */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
                <div className="bg-slate-800 rounded p-3">
                  <div className="text-xs text-slate-400">Total reseñas</div>
                  <div className="text-lg">{sentiment.summary?.total ?? 0}</div>
                </div>
                <div className="bg-slate-800 rounded p-3">
                  <div className="text-xs text-slate-400">Promedio puntaje</div>
                  <div className="text-lg">{Number(sentiment.summary?.avg_score ?? 0).toFixed(3)}</div>
                </div>
                <div className="bg-slate-800 rounded p-3">
                  <div className="text-xs text-slate-400">Positivo</div>
                  <div className="text-lg">{sentiment.summary?.counts?.positivo ?? 0}</div>
                </div>
                <div className="bg-slate-800 rounded p-3">
                  <div className="text-xs text-slate-400">Negativo</div>
                  <div className="text-lg">{sentiment.summary?.counts?.negativo ?? 0}</div>
                </div>
              </div>

              {/* Figuras */}
              {sentiment.figures?.length ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {sentiment.figures.map((fig, idx) => (
                    <div key={idx} className="bg-slate-800 rounded p-2">
                      <img
                        alt={`Sentimiento ${idx+1}`}
                        className="rounded border border-slate-700"
                        crossOrigin="anonymous"
                        src={buildFileUrl(fig, `s-${idx}`)}
                        onError={(e) => { e.currentTarget.src = buildFileUrl(fig, `s-${idx}-retry`); }}
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-400 text-sm">Sin figuras de sentimientos.</p>
              )}

              {/* Enlaces a tablas */}
              <div className="text-sm space-x-2">
                {sentiment.tables?.summary_json ? (
                  <a className="text-indigo-400 hover:underline" href={`http://localhost:5000/api/reports/file?path=${encodeURIComponent(sentiment.tables.summary_json)}`} target="_blank" rel="noreferrer">Resumen (JSON)</a>
                ) : null}
                {sentiment.tables?.detailed_csv ? (
                  <a className="text-indigo-400 hover:underline" href={`http://localhost:5000/api/reports/file?path=${encodeURIComponent(sentiment.tables.detailed_csv)}`} target="_blank" rel="noreferrer">Detalle (CSV)</a>
                ) : null}
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Sin reporte de sentimientos.</p>
          )}
        </section>

        {/* Figuras numéricas generadas */}
        <section className="bg-slate-900 p-4 rounded border border-slate-800">
          <h3 className="text-lg font-medium mb-2">Figuras numéricas</h3>
          {numeric?.figures?.length ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              {numeric.figures.map((fig, idx) => (
                <div key={idx} className="bg-slate-800 rounded p-2">
                  <img
                    alt={`Figura ${idx+1}`}
                    className="rounded border border-slate-700"
                    crossOrigin="anonymous"
                    src={buildFileUrl(fig, `n-${idx}`)}
                    onError={(e) => { e.currentTarget.src = buildFileUrl(fig, `n-${idx}-retry`); }}
                  />
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-400 text-sm">No hay figuras numéricas disponibles.</p>
          )}
        </section>
      </div>

      {/* Exportación Backend */}
      <section className="mt-6 bg-slate-900 p-4 rounded border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-medium">Exportación Backend</h3>
          <button onClick={onExportBackend} className="px-3 py-2 bg-slate-700 rounded hover:bg-slate-600">Exportar (backend)</button>
        </div>
        {exportInfo ? (
          <div className="space-y-2 text-sm">
            <div className="text-slate-400">Directorio: {exportInfo.export_root}</div>
            <div>
              <span className="font-medium">Resumen: </span>
              <a className="text-indigo-400 hover:underline" href={`http://localhost:5000/api/reports/file?path=${encodeURIComponent(exportInfo.summary_path)}`} target="_blank" rel="noreferrer">Abrir JSON</a>
            </div>
            <div>
              <span className="font-medium">Tabla perfiles numéricos (CSV): </span>
              <a className="text-indigo-400 hover:underline" href={`http://localhost:5000/api/reports/file?path=${encodeURIComponent(exportInfo.sections.numeric_profiles.tables.summary_csv)}`} target="_blank" rel="noreferrer">Descargar</a>
            </div>
            <div>
              <span className="font-medium">Num. figuras: </span>
              <span>{exportInfo.sections.numeric_profiles.figures?.length || 0}</span>
            </div>
            {exportInfo.sections.numeric_profiles.figures?.length ? (
              <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-2">
                {exportInfo.sections.numeric_profiles.figures.map((fig, idx) => (
                  <a key={idx} href={`http://localhost:5000/api/reports/file?path=${encodeURIComponent(fig)}&cb=${Date.now()}`} target="_blank" rel="noreferrer" className="block">
                    <img alt={`Figura ${idx+1}`} className="rounded border border-slate-700" crossOrigin="anonymous" src={`http://localhost:5000/api/reports/file?path=${encodeURIComponent(fig)}&cb=${Date.now()}`} />
                  </a>
                ))}
              </div>
            ) : null}
            <div>
              <span className="font-medium">Patrones textuales (JSON): </span>
              <a className="text-indigo-400 hover:underline" href={`http://localhost:5000/api/reports/file?path=${encodeURIComponent(exportInfo.sections.text_patterns.tables_json)}`} target="_blank" rel="noreferrer">Abrir JSON</a>
            </div>
          </div>
        ) : (
          <p className="text-slate-400 text-sm">Aún no se ha exportado. Usa el botón para generar archivos en el backend.</p>
        )}
      </section>
    </div>
  );
}
