from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import json

from models import DataStore, ModelStore

training_bp = Blueprint("training", __name__)


def _get_features_for_clustering(df: pd.DataFrame) -> pd.DataFrame:
    """Preparar características para clustering de clientes"""
    # Seleccionar solo columnas numéricas relevantes
    feature_cols = [
        "frecuencia_compra",
        "monto_total_gastado",
        "monto_promedio_compra",
        "dias_desde_ultima_compra",
        "antiguedad_cliente_meses",
        "numero_productos_distintos",
        "canal_encoded",
    ]
    
    available_cols = [col for col in feature_cols if col in df.columns]
    return df[available_cols].copy()


def _find_optimal_k(data: np.ndarray, max_k: int = 10) -> int:
    """Encontrar número óptimo de clusters usando el método del codo"""
    inertias = []
    silhouette_scores = []
    k_range = range(2, max_k + 1)

    for k in k_range:
        kmeans = KMeans(
            n_clusters=k,
            init="k-means++",
            n_init=10,
            random_state=42,
            max_iter=300,
        )
        kmeans.fit(data)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(data, kmeans.labels_))

    # Usar silhouette score para encontrar el óptimo
    optimal_k = list(k_range)[np.argmax(silhouette_scores)]
    
    ModelStore.optimal_k = optimal_k
    return optimal_k


@training_bp.post("/train/kmeans")
def train_kmeans():
    """Entrenar modelo K-means para segmentación de clientes"""
    if DataStore.df_preprocessed is None:
        return jsonify({"error": "Los datos no han sido preprocesados aún"}), 400

    try:
        # Obtener características para clustering
        features = _get_features_for_clustering(DataStore.df_preprocessed)
        
        if len(features) < 2:
            return jsonify({"error": "Datos insuficientes para entrenar el modelo"}), 400

        # Normalizar características
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        DataStore.scaler_for_models = scaler

        # Obtener parámetros del modelo
        n_clusters = ModelStore.kmeans_params.get("n_clusters", 3)

        # Entrenar K-means
        kmeans = KMeans(
            n_clusters=n_clusters,
            init=ModelStore.kmeans_params.get("init", "k-means++"),
            n_init=ModelStore.kmeans_params.get("n_init", 10),
            max_iter=ModelStore.kmeans_params.get("max_iter", 300),
            random_state=ModelStore.kmeans_params.get("random_state", 42),
        )

        labels = kmeans.fit_predict(features_scaled)
        ModelStore.kmeans_model = kmeans
        ModelStore.kmeans_labels = labels.tolist()

        # Calcular métricas
        silhouette = silhouette_score(features_scaled, labels)
        davies_bouldin = davies_bouldin_score(features_scaled, labels)
        calinski_harabasz = calinski_harabasz_score(features_scaled, labels)

        # Agregar etiquetas al dataframe preprocesado
        df_with_labels = DataStore.df_preprocessed.copy()
        df_with_labels["kmeans_cluster"] = labels

        return jsonify({
            "success": True,
            "message": "Modelo K-means entrenado exitosamente",
            "model_info": {
                "algorithm": "K-means",
                "n_clusters": int(n_clusters),
                "n_features": features_scaled.shape[1],
                "n_samples": features_scaled.shape[0],
            },
            "metrics": {
                "inertia": float(kmeans.inertia_),
                "silhouette_score": float(silhouette),
                "davies_bouldin_score": float(davies_bouldin),
                "calinski_harabasz_score": float(calinski_harabasz),
            },
            "cluster_distribution": {
                str(i): int(np.sum(np.array(labels) == i))
                for i in range(n_clusters)
            }
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error al entrenar K-means",
            "detail": str(e)
        }), 500


@training_bp.post("/train/hierarchical")
def train_hierarchical():
    """Entrenar modelo Hierarchical Clustering para segmentación de clientes"""
    if DataStore.df_preprocessed is None:
        return jsonify({"error": "Los datos no han sido preprocesados aún"}), 400

    try:
        # Obtener características para clustering
        features = _get_features_for_clustering(DataStore.df_preprocessed)
        
        if len(features) < 2:
            return jsonify({"error": "Datos insuficientes para entrenar el modelo"}), 400

        # Normalizar características
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        # Obtener parámetros del modelo
        n_clusters = ModelStore.hierarchical_params.get("n_clusters", 3)
        linkage = ModelStore.hierarchical_params.get("linkage", "ward")

        # Entrenar Hierarchical Clustering
        hierarchical = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage=linkage,
        )

        labels = hierarchical.fit_predict(features_scaled)
        ModelStore.hierarchical_model = hierarchical
        ModelStore.hierarchical_labels = labels.tolist()

        # Calcular métricas
        silhouette = silhouette_score(features_scaled, labels)
        davies_bouldin = davies_bouldin_score(features_scaled, labels)
        calinski_harabasz = calinski_harabasz_score(features_scaled, labels)

        # Agregar etiquetas al dataframe preprocesado
        df_with_labels = DataStore.df_preprocessed.copy()
        df_with_labels["hierarchical_cluster"] = labels

        return jsonify({
            "success": True,
            "message": "Modelo Hierarchical Clustering entrenado exitosamente",
            "model_info": {
                "algorithm": "Hierarchical Clustering",
                "n_clusters": int(n_clusters),
                "linkage": linkage,
                "n_features": features_scaled.shape[1],
                "n_samples": features_scaled.shape[0],
            },
            "metrics": {
                "silhouette_score": float(silhouette),
                "davies_bouldin_score": float(davies_bouldin),
                "calinski_harabasz_score": float(calinski_harabasz),
            },
            "cluster_distribution": {
                str(i): int(np.sum(np.array(labels) == i))
                for i in range(n_clusters)
            }
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error al entrenar Hierarchical Clustering",
            "detail": str(e)
        }), 500


@training_bp.post("/train/auto-k")
def train_with_auto_k():
    """Entrenar K-means con número óptimo de clusters determinado automáticamente"""
    if DataStore.df_preprocessed is None:
        return jsonify({"error": "Los datos no han sido preprocesados aún"}), 400

    try:
        # Obtener características para clustering
        features = _get_features_for_clustering(DataStore.df_preprocessed)
        
        if len(features) < 2:
            return jsonify({"error": "Datos insuficientes para entrenar el modelo"}), 400

        # Normalizar características
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        # Encontrar K óptimo
        max_k = min(10, len(features) - 1)
        optimal_k = _find_optimal_k(features_scaled, max_k=max_k)

        # Entrenar K-means con K óptimo
        kmeans = KMeans(
            n_clusters=optimal_k,
            init="k-means++",
            n_init=10,
            max_iter=300,
            random_state=42,
        )

        labels = kmeans.fit_predict(features_scaled)
        ModelStore.kmeans_model = kmeans
        ModelStore.kmeans_labels = labels.tolist()
        ModelStore.kmeans_params["n_clusters"] = optimal_k

        # Calcular métricas
        silhouette = silhouette_score(features_scaled, labels)
        davies_bouldin = davies_bouldin_score(features_scaled, labels)
        calinski_harabasz = calinski_harabasz_score(features_scaled, labels)

        return jsonify({
            "success": True,
            "message": f"K-means entrenado con K automático ({optimal_k})",
            "model_info": {
                "algorithm": "K-means (Auto K)",
                "n_clusters": int(optimal_k),
                "n_features": features_scaled.shape[1],
                "n_samples": features_scaled.shape[0],
            },
            "metrics": {
                "inertia": float(kmeans.inertia_),
                "silhouette_score": float(silhouette),
                "davies_bouldin_score": float(davies_bouldin),
                "calinski_harabasz_score": float(calinski_harabasz),
            },
            "cluster_distribution": {
                str(i): int(np.sum(np.array(labels) == i))
                for i in range(optimal_k)
            }
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error al entrenar K-means con K automático",
            "detail": str(e)
        }), 500


@training_bp.get("/models/status")
def get_models_status():
    """Obtener estado de los modelos entrenados"""
    status = {
        "kmeans": {
            "trained": ModelStore.kmeans_model is not None,
            "n_clusters": ModelStore.kmeans_params.get("n_clusters"),
            "labels_count": len(ModelStore.kmeans_labels) if ModelStore.kmeans_labels else 0,
        },
        "hierarchical": {
            "trained": ModelStore.hierarchical_model is not None,
            "n_clusters": ModelStore.hierarchical_params.get("n_clusters"),
            "labels_count": len(ModelStore.hierarchical_labels) if ModelStore.hierarchical_labels else 0,
        },
        "optimal_k": ModelStore.optimal_k,
    }

    return jsonify(status), 200
