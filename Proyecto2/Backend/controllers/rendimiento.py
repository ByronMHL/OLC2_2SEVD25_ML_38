from flask import Blueprint, jsonify
import numpy as np
from typing import Any, Dict, List, Optional
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

from models import DataStore, ModelStore
from controllers.training import preprocess_dataframe

rendimiento_bp = Blueprint("rendimiento", __name__)


def _safe_len(arr: Any) -> int:
    try:
        return len(arr)
    except Exception:
        return 0


def _compute_metrics(X: np.ndarray, labels: List[int], metric: Optional[str] = None) -> Dict[str, float]:
    """Calcula métricas internas con defensas.

    - Silhouette: requiere >= 2 clusters y n_samples >= 3.
    - Davies-Bouldin y Calinski-Harabasz: requieren >= 2 clusters.
    - `metric` solo aplica a silhouette (e.g., 'cosine' para texto).
    """
    n_samples = X.shape[0] if hasattr(X, "shape") else _safe_len(X)
    k = len(set(labels))
    result = {
        "silhouette_score": None,
        "davies_bouldin_score": None,
        "calinski_harabasz_score": None,
    }

    if k < 2 or n_samples < 3:
        return result

    try:
        if metric:
            result["silhouette_score"] = float(silhouette_score(X, labels, metric=metric))
        else:
            result["silhouette_score"] = float(silhouette_score(X, labels))
    except Exception:
        result["silhouette_score"] = None

    try:
        result["davies_bouldin_score"] = float(davies_bouldin_score(X, labels))
    except Exception:
        result["davies_bouldin_score"] = None

    try:
        result["calinski_harabasz_score"] = float(calinski_harabasz_score(X, labels))
    except Exception:
        result["calinski_harabasz_score"] = None

    return result


@rendimiento_bp.get("/evaluation/clustering")
def evaluate_clustering_models():
    """Evalúa modelos de clustering entrenados usando métricas internas.

    - No entrena modelos; solo evalúa los existentes.
    - Usa distancia 'euclidean' para numéricos y 'cosine' para texto (en silhouette).
    """
    evaluations: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []

    # 1) K-Means numérico
    if ModelStore.kmeans_model is not None and ModelStore.kmeans_labels:
        try:
            X_num = preprocess_dataframe()
            labels = ModelStore.kmeans_labels
            if _safe_len(labels) != _safe_len(X_num):
                errors.append({"model": "K-means", "error": "Desalineación entre X y etiquetas"})
            else:
                metrics = _compute_metrics(X_num, labels)
                evaluations.append({
                    "model": "K-means",
                    "n_clusters": int(getattr(ModelStore.kmeans_model, "n_clusters", len(set(labels)))),
                    **metrics,
                })
        except Exception as e:
            errors.append({"model": "K-means", "error": str(e)})
    else:
        errors.append({"model": "K-means", "error": "Modelo no entrenado"})

    # 2) Hierarchical Clustering
    if ModelStore.hierarchical_model is not None and ModelStore.hierarchical_labels:
        try:
            X_num = preprocess_dataframe()
            labels = ModelStore.hierarchical_labels
            if _safe_len(labels) != _safe_len(X_num):
                errors.append({"model": "Hierarchical", "error": "Desalineación entre X y etiquetas"})
            else:
                metrics = _compute_metrics(X_num, labels)
                evaluations.append({
                    "model": "Hierarchical Clustering",
                    "n_clusters": int(getattr(ModelStore.hierarchical_model, "n_clusters", len(set(labels)))),
                    **metrics,
                })
        except Exception as e:
            errors.append({"model": "Hierarchical Clustering", "error": str(e)})
    else:
        errors.append({"model": "Hierarchical Clustering", "error": "Modelo no entrenado"})

    # 3) K-Means textual (TF-IDF)
    if ModelStore.text_kmeans_model is not None and ModelStore.text_kmeans_labels:
        try:
            # Usar el vectorizador entrenado para obtener la misma representación
            vectorizer = getattr(ModelStore, "text_vectorizer", None)
            if vectorizer is None:
                raise ValueError("Vectorizador TF-IDF no disponible; entrene /training/text/kmeans primero")
            if getattr(DataStore, "df_text_cleaned", None) is None:
                raise ValueError("No hay datos textuales limpios. Ejecute /clean-text primero")
            df = DataStore.df_text_cleaned
            if "texto_limpio" not in df.columns:
                raise ValueError("La columna 'texto_limpio' no está disponible")
            X_text = vectorizer.transform(df["texto_limpio"].tolist()).toarray()
            labels = ModelStore.text_kmeans_labels
            if _safe_len(labels) != _safe_len(X_text):
                errors.append({"model": "K-means (Text)", "error": "Desalineación entre X y etiquetas"})
            else:
                metrics = _compute_metrics(X_text, labels, metric="cosine")
                evaluations.append({
                    "model": "K-means (Text TF-IDF)",
                    "n_clusters": int(getattr(ModelStore.text_kmeans_model, "n_clusters", len(set(labels)))),
                    **metrics,
                })
        except Exception as e:
            errors.append({"model": "K-means (Text TF-IDF)", "error": str(e)})
    else:
        errors.append({"model": "K-means (Text TF-IDF)", "error": "Modelo no entrenado"})

    # 4) Auto K-Means (si existe óptimo y modelo/etiquetas disponibles)
    if ModelStore.optimal_k and ModelStore.kmeans_auto_model is not None and ModelStore.kmeans_auto_labels:
        try:
            # Usa el mismo X numérico y las etiquetas de Auto-K
            X_num = preprocess_dataframe()
            labels = ModelStore.kmeans_auto_labels or []
            if _safe_len(labels) != _safe_len(X_num):
                errors.append({"model": "K-means (Auto-K)", "error": "Desalineación entre X y etiquetas"})
            else:
                metrics = _compute_metrics(X_num, labels)
                evaluations.append({
                    "model": "K-means (Auto-K)",
                    "n_clusters": int(ModelStore.optimal_k),
                    **metrics,
                })
        except Exception as e:
            errors.append({"model": "K-means (Auto-K)", "error": str(e)})

    if not evaluations:
        return jsonify({
            "success": False,
            "error": "No hay modelos entrenados para evaluar",
            "details": errors,
        }), 400

    return jsonify({
        "success": True,
        "evaluations": evaluations,
        "errors": errors,
    }), 200


@rendimiento_bp.get("/evaluation/clustering/kmeans")
def evaluate_kmeans():
    """Evalúa K-Means numérico si está entrenado."""
    if ModelStore.kmeans_model is None or not ModelStore.kmeans_labels:
        return jsonify({"success": False, "error": "K-means no entrenado"}), 400
    try:
        X_num = preprocess_dataframe()
        labels = ModelStore.kmeans_labels
        if _safe_len(labels) != _safe_len(X_num):
            return jsonify({"success": False, "error": "Desalineación entre X y etiquetas"}), 400
        metrics = _compute_metrics(X_num, labels)
        return jsonify({
            "success": True,
            "evaluation": {
                "model": "K-means",
                "n_clusters": int(getattr(ModelStore.kmeans_model, "n_clusters", len(set(labels)))),
                **metrics,
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@rendimiento_bp.get("/evaluation/clustering/hierarchical")
def evaluate_hierarchical():
    """Evalúa Hierarchical Clustering si está entrenado."""
    if ModelStore.hierarchical_model is None or not ModelStore.hierarchical_labels:
        return jsonify({"success": False, "error": "Hierarchical Clustering no entrenado"}), 400
    try:
        X_num = preprocess_dataframe()
        labels = ModelStore.hierarchical_labels
        if _safe_len(labels) != _safe_len(X_num):
            return jsonify({"success": False, "error": "Desalineación entre X y etiquetas"}), 400
        metrics = _compute_metrics(X_num, labels)
        return jsonify({
            "success": True,
            "evaluation": {
                "model": "Hierarchical Clustering",
                "n_clusters": int(getattr(ModelStore.hierarchical_model, "n_clusters", len(set(labels)))),
                **metrics,
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@rendimiento_bp.get("/evaluation/clustering/text")
def evaluate_text_kmeans():
    """Evalúa K-Means textual (TF-IDF) si está entrenado."""
    if ModelStore.text_kmeans_model is None or not ModelStore.text_kmeans_labels:
        return jsonify({"success": False, "error": "K-means (Text TF-IDF) no entrenado"}), 400
    try:
        vectorizer = getattr(ModelStore, "text_vectorizer", None)
        if vectorizer is None:
            return jsonify({"success": False, "error": "Vectorizador TF-IDF no disponible"}), 400
        if getattr(DataStore, "df_text_cleaned", None) is None:
            return jsonify({"success": False, "error": "No hay datos textuales limpios. Ejecute /clean-text"}), 400
        df = DataStore.df_text_cleaned
        if "texto_limpio" not in df.columns:
            return jsonify({"success": False, "error": "La columna 'texto_limpio' no está disponible"}), 400
        X_text = vectorizer.transform(df["texto_limpio"].tolist()).toarray()
        labels = ModelStore.text_kmeans_labels
        if _safe_len(labels) != _safe_len(X_text):
            return jsonify({"success": False, "error": "Desalineación entre X y etiquetas"}), 400
        metrics = _compute_metrics(X_text, labels, metric="cosine")
        return jsonify({
            "success": True,
            "evaluation": {
                "model": "K-means (Text TF-IDF)",
                "n_clusters": int(getattr(ModelStore.text_kmeans_model, "n_clusters", len(set(labels)))),
                **metrics,
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@rendimiento_bp.get("/evaluation/clustering/auto-k")
def evaluate_auto_kmeans():
    """Evalúa K-Means Auto-K si existe óptimo y etiquetas actuales."""
    if not ModelStore.optimal_k:
        return jsonify({"success": False, "error": "Auto-K no disponible (optimal_k no definido)"}), 400
    if ModelStore.kmeans_auto_model is None or not ModelStore.kmeans_auto_labels:
        return jsonify({"success": False, "error": "No hay modelo/etiquetas de Auto-K entrenados"}), 400
    try:
        X_num = preprocess_dataframe()
        labels = ModelStore.kmeans_auto_labels
        if _safe_len(labels) != _safe_len(X_num):
            return jsonify({"success": False, "error": "Desalineación entre X y etiquetas"}), 400
        metrics = _compute_metrics(X_num, labels)
        return jsonify({
            "success": True,
            "evaluation": {
                "model": "K-means (Auto-K)",
                "n_clusters": int(ModelStore.optimal_k),
                **metrics,
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
