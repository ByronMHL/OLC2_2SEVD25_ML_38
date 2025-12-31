import os
import json
from typing import Dict, Any, List
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Estilo consistente y legible para figuras
sns.set_theme(style="darkgrid", palette="deep")

from models import DataStore, ModelStore


def _ensure_dirs(base_dir: str) -> Dict[str, str]:
    figures_dir = os.path.join(base_dir, "figures")
    tables_dir = os.path.join(base_dir, "tables")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)
    return {"figures": figures_dir, "tables": tables_dir}


def compute_text_patterns(top_n: int = 12, base_dir: str = "exports", use_subdir: bool = True) -> Dict[str, Any]:
    """Extrae términos clave por cluster a partir del centroide de KMeans y TF-IDF."""
    if ModelStore.text_kmeans_model is None or ModelStore.text_vectorizer is None:
        raise ValueError("No hay modelo textual entrenado ni vectorizador. Ejecute /training/text/kmeans.")
    if getattr(DataStore, "df_text_cleaned", None) is None:
        raise ValueError("No hay datos textuales limpios disponibles.")

    kmeans = ModelStore.text_kmeans_model
    vectorizer = ModelStore.text_vectorizer
    centers = kmeans.cluster_centers_  # shape (k, vocab)

    vocab = np.array(sorted(vectorizer.vocabulary_.items(), key=lambda x: x[1], reverse=False))
    # vocab entries: [ (term, idx), ... ] sorted by idx ascending
    terms = vocab[:, 0]

    if not os.path.isabs(base_dir):
        base_dir = os.path.join(os.path.dirname(__file__), base_dir)
    run_dir = base_dir
    if use_subdir:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(base_dir, run_id)
    dirs = _ensure_dirs(run_dir)

    patterns: Dict[str, Any] = {"clusters": {}}

    for cl in range(centers.shape[0]):
        weights = centers[cl]
        top_idx = np.argsort(weights)[::-1][:top_n]
        top_terms = terms[top_idx]
        top_weights = weights[top_idx]

        # Gráfico de barras de términos
        plt.figure(figsize=(10, 4))
        sns.barplot(x=list(top_terms), y=list(top_weights), color="#72B7B2")
        plt.title(f"Términos clave - Cluster {cl}")
        plt.xlabel("Términos")
        plt.ylabel("Peso (centroide)")
        plt.xticks(rotation=45, ha='right')
        path = os.path.join(dirs["figures"], f"text_top_terms_cluster_{cl}.png")
        plt.tight_layout()
        plt.savefig(path, transparent=False)
        plt.close()

        patterns["clusters"][str(cl)] = {
            "top_terms": [{"term": str(t), "weight": float(w)} for t, w in zip(top_terms, top_weights)],
            "figure": path,
        }

    # Guardar JSON
    json_path = os.path.join(dirs["tables"], "text_patterns.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)

    patterns["tables_json"] = json_path
    patterns["run_dir"] = run_dir
    return patterns
