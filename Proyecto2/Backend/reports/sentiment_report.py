import os
import json
from typing import Dict, Any
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="darkgrid", palette="deep")

from models import DataStore
from utils.analisis_sentimiento import analyze_sentiments, summarize_sentiments


def _ensure_dirs(base_dir: str) -> Dict[str, str]:
    figures_dir = os.path.join(base_dir, "figures")
    tables_dir = os.path.join(base_dir, "tables")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)
    return {"figures": figures_dir, "tables": tables_dir}


def compute_sentiment_report(base_dir: str = "exports", use_subdir: bool = True) -> Dict[str, Any]:
    """Genera reporte de sentimientos independiente del clustering a partir de `df_text_cleaned`.

    - Devuelve resumen (conteos y promedio), paths a figuras y tablas.
    """
    if getattr(DataStore, "df_text_cleaned", None) is None:
        raise ValueError("No hay datos textuales limpios disponibles. Ejecute /clean-text primero.")

    df_text = DataStore.df_text_cleaned.copy()

    # Usar base_dir (permitiendo rutas absolutas o relativas)
    if not os.path.isabs(base_dir):
        base_dir = os.path.join(os.path.dirname(__file__), base_dir)
    run_dir = base_dir
    if use_subdir:
        import datetime
        run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(base_dir, run_id)
    dirs = _ensure_dirs(run_dir)

    # Calcular sentimiento por reseña
    df_sent = analyze_sentiments(df_text)

    # Guardar detalle CSV (sin índices sensibles, usar índice como fila original)
    detailed_csv = os.path.join(dirs["tables"], "sentiment_detailed.csv")
    df_out = df_sent[["texto_limpio", "sentiment_score", "sentiment_label"]].copy()
    # Renombrar para claridad
    df_out = df_out.rename(columns={
        "texto_limpio": "texto",
    })
    df_out.to_csv(detailed_csv, index=True)

    # Resumen
    summary = summarize_sentiments(df_sent)
    summary_json = os.path.join(dirs["tables"], "sentiment_summary.json")
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Figuras: histograma de puntajes y barras de etiquetas
    figures = []

    plt.figure(figsize=(8, 4))
    sns.histplot(df_sent["sentiment_score"], bins=20, kde=True, color="#4C78A8")
    plt.title("Distribución de puntajes de sentimiento")
    plt.xlabel("Puntaje")
    plt.ylabel("Frecuencia")
    hist_path = os.path.join(dirs["figures"], "sentiment_score_hist.png")
    plt.tight_layout()
    plt.savefig(hist_path, transparent=False)
    plt.close()
    figures.append(hist_path)

    plt.figure(figsize=(6, 4))
    counts = df_sent["sentiment_label"].value_counts()
    sns.barplot(x=counts.index.astype(str), y=counts.values, color="#72B7B2")
    plt.title("Conteo por etiqueta de sentimiento")
    plt.xlabel("Etiqueta")
    plt.ylabel("Cantidad")
    bar_path = os.path.join(dirs["figures"], "sentiment_label_counts.png")
    plt.tight_layout()
    plt.savefig(bar_path, transparent=False)
    plt.close()
    figures.append(bar_path)

    result = {
        "summary": summary,
        "tables": {
            "detailed_csv": detailed_csv,
            "summary_json": summary_json,
        },
        "figures": figures,
        "run_dir": run_dir,
    }

    # Guardar JSON completo del reporte
    json_path = os.path.join(dirs["tables"], "sentiment_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    result["tables"]["report_json"] = json_path

    return result
