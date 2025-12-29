from typing import Optional, Any, Dict, List
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class DataStore:
    """Almacenamiento global de datos"""
    df_raw: Optional[pd.DataFrame] = None
    df_cleaned: Optional[pd.DataFrame] = None
    df_reviews: Optional[pd.DataFrame] = None
    scaler: Optional[StandardScaler] = None


class ModelStore:
    """Almacenamiento de modelos de clustering entrenados"""
    kmeans_model: Optional[KMeans] = None
    hierarchical_model: Optional[Any] = None  # AgglomerativeClustering
    kmeans_labels: Optional[List[int]] = None
    hierarchical_labels: Optional[List[int]] = None
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
