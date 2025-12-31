from typing import Optional, Any, Dict, List
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except Exception:
    TfidfVectorizer = Any  # fallback typing


class DataStore:
    """Almacenamiento global de datos"""
    df_raw: Optional[pd.DataFrame] = None
    # Compatibilidad previa
    df_cleaned: Optional[pd.DataFrame] = None
    df_reviews: Optional[pd.DataFrame] = None
    # Nuevos pipelines separados
    df_numeric_cleaned: Optional[pd.DataFrame] = None
    df_text_cleaned: Optional[pd.DataFrame] = None
    scaler: Optional[StandardScaler] = None


class ModelStore:
    """Almacenamiento de modelos de clustering entrenados"""
    kmeans_model: Optional[KMeans] = None
    hierarchical_model: Optional[Any] = None  # AgglomerativeClustering
    kmeans_labels: Optional[List[int]] = None
    hierarchical_labels: Optional[List[int]] = None
    # Separación de Auto-K para evitar sobrescribir el K-Means manual
    kmeans_auto_model: Optional[KMeans] = None
    kmeans_auto_labels: Optional[List[int]] = None
    kmeans_params: Dict[str, Any] = {
        "n_clusters":7,
        "init": "k-means++",
        "n_init": 10,
        "max_iter":300,
        "random_state": 42,
    }
    hierarchical_params: Dict[str, Any] = {
        "n_clusters": 7,
        "linkage": "ward",
    }
    optimal_k: Optional[int] = None
    scaler_for_models: Optional[StandardScaler] = None

    # Modelos para clustering textual
    text_kmeans_model: Optional[KMeans] = None
    text_kmeans_labels: Optional[List[int]] = None
    text_vectorizer: Optional[Any] = None
    text_kmeans_params: Dict[str, Any] = {
        "n_clusters": 2,
        "init": "k-means++",
        "n_init": 20,
        "max_iter": 600,
        "random_state": 42,
        # Parámetros TF-IDF opcionales
        "tfidf_max_features": 2000,
        "tfidf_min_df": 3,
        "tfidf_max_df": 0.7,
        # Nuevos parámetros TF-IDF
        "ngram_range": (1, 2),
        "sublinear_tf": True,
        "norm": "l2",
    }
