from flask import Blueprint, jsonify
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.feature_extraction.text import TfidfVectorizer

from models import DataStore, ModelStore

training_text_bp = Blueprint("training_text", __name__)


def _preprocess_text_to_tfidf():
    """Convierte `df_text_cleaned` a matriz TF-IDF (densa) para clustering textual."""
    if getattr(DataStore, 'df_text_cleaned', None) is None:
        raise ValueError("Primero ejecute la limpieza textual (/clean-text)")

    df = DataStore.df_text_cleaned.copy()
    if "texto_limpio" not in df.columns:
        raise ValueError("La columna 'texto_limpio' no está disponible tras la limpieza textual")

    params = ModelStore.text_kmeans_params
    vectorizer = TfidfVectorizer(
        max_features=params.get("tfidf_max_features", 2000),
        min_df=params.get("tfidf_min_df", 3),
        max_df=params.get("tfidf_max_df", 0.7),
        ngram_range=tuple(params.get("ngram_range", (1, 2))),
        sublinear_tf=bool(params.get("sublinear_tf", True)),
        norm=(None if (str(params.get("norm", "l2")).lower() in ["none", "null", "none"] or params.get("norm") is None) else str(params.get("norm", "l2")))
    )

    X_tfidf = vectorizer.fit_transform(df["texto_limpio"].tolist())
    # KMeans requiere denso
    X_dense = X_tfidf.toarray()
    return X_dense, vectorizer


@training_text_bp.get("/training/text/kmeans")
def train_text_kmeans():
    """Entrena KMeans sobre TF-IDF de `df_text_cleaned`."""
    try:
        X_dense, vectorizer = _preprocess_text_to_tfidf()
        n_clusters = ModelStore.text_kmeans_params.get("n_clusters", 6)
        kmeans = KMeans(
            n_clusters=n_clusters,
            init=ModelStore.text_kmeans_params.get("init", "k-means++"),
            n_init=ModelStore.text_kmeans_params.get("n_init", 10),
            max_iter=ModelStore.text_kmeans_params.get("max_iter", 500),
            random_state=ModelStore.text_kmeans_params.get("random_state", 42),
        )
        labels = kmeans.fit_predict(X_dense)
        ModelStore.text_kmeans_model = kmeans
        ModelStore.text_kmeans_labels = labels.tolist()
        # Guardar vectorizador para análisis de patrones
        ModelStore.text_vectorizer = vectorizer
        # Añadir etiquetas al dataframe textual
        if getattr(DataStore, 'df_text_cleaned', None) is not None:
            try:
                DataStore.df_text_cleaned["text_cluster"] = labels
            except Exception:
                pass

        # Métricas (usar cosine para texto)
        silhouette = silhouette_score(X_dense, labels, metric='cosine')
        davies_bouldin = davies_bouldin_score(X_dense, labels)
        calinski_harabasz = calinski_harabasz_score(X_dense, labels)

        return jsonify({
            "success": True,
            "message": "Clustering textual (TF-IDF + KMeans) entrenado exitosamente",
            "model_info": {
                "algorithm": "K-means (Text TF-IDF)",
                "n_clusters": int(n_clusters),
                "n_features": int(X_dense.shape[1]),
                "n_samples": int(X_dense.shape[0]),
                "vocab_size": int(len(vectorizer.vocabulary_)),
            },
            "metrics": {
                "inertia": float(kmeans.inertia_),
                "silhouette_score_cosine": float(silhouette),
                "davies_bouldin_score": float(davies_bouldin),
                "calinski_harabasz_score": float(calinski_harabasz),
            },
            "cluster_distribution": {
                str(i): int(np.sum(np.array(labels) == i))
                for i in range(n_clusters)
            }
        }), 200
    except ValueError as ve:
        return jsonify({
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Error al entrenar KMeans textual",
            "detail": str(e)
        }), 500
