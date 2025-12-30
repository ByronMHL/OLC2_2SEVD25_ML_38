from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import os

from models import DataStore, ModelStore
from utils.modelsStatus import build_models_status

training_bp = Blueprint("training", __name__)


def _find_optimal_k(data: np.ndarray, max_k: int = 10) -> int:
    # Método mixto: calcula inercia (codo) para todos los k válidos y usa silhouette para seleccionar k óptimo.
    n_samples = data.shape[0]
    upper_k = max(1, min(max_k, n_samples - 1))
    k_range = range(1, upper_k + 1)

    inertias = []
    silhouette_scores = []
    silhouette_ks = []

    for k in k_range:
        kmeans = KMeans(
            n_clusters=k,
            init="k-means++",
            n_init=10,
            random_state=42,
            max_iter=500,
        )
        labels = kmeans.fit_predict(data)
        inertias.append(kmeans.inertia_)
        # Silhouette solo es válido para k >= 2
        if k >= 2:
            silhouette_scores.append(silhouette_score(data, labels))
            silhouette_ks.append(k)

    if silhouette_scores:
        optimal_k = silhouette_ks[int(np.argmax(silhouette_scores))]
    else:
        # Fallback seguro si no hay suficientes muestras para silhouette
        optimal_k = max(2, 1)

    ModelStore.optimal_k = optimal_k
    return optimal_k

def preprocess_dataframe() -> np.ndarray:
    # Verificar datos limpios disponibles
    if getattr(DataStore, 'df_numeric_cleaned', None) is None:
        raise ValueError("Primero ejecute la limpieza numérica (/clean)")

    df = DataStore.df_numeric_cleaned.copy()

    # Columnas numéricas esperadas (usar solo las presentes)
    expected_num_cols = [
        "frecuencia_compra",
        "monto_total_gastado",
        "monto_promedio_compra",
        "dias_desde_ultima_compra",
        "antiguedad_cliente_meses",
        "numero_productos_distintos",
    ]
    num_cols = [c for c in expected_num_cols if c in df.columns]

    # Quitar columnas categóricas si existen (se omiten en este pipeline)
    for col in ["producto_categoria", "canal_principal"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    if len(num_cols) == 0:
        raise ValueError("No hay columnas numéricas válidas para el preprocesado")

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_cols),
            # ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
        ]
    )

    X_processed = preprocessor.fit_transform(df)
    return X_processed

    # 4. Visualización PCA (Reducción a 2D para graficar)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_processed)
    df_pca = pd.DataFrame(data=X_pca, columns=['Componente 1', 'Componente 2'])
    df_pca['Cluster'] = DataStore.df_cleaned['cluster']

    # Generar Gráficas
    fig, ax = plt.subplots(1, 2, figsize=(18, 6))

    # Gráfica del Codo
    ax[0].plot(range(1, 11), inertias, marker='o', linestyle='--')
    ax[0].set_title('Método del Codo')
    ax[0].set_xlabel('Número de Clusters')
    ax[0].set_ylabel('Inercia (WCSS)')
    ax[0].grid(True)

    # Gráfica de Clusters (PCA)
    sns.scatterplot(x='Componente 1', y='Componente 2', hue='Cluster', palette='viridis', data=df_pca, s=100, ax=ax[1])
    ax[1].set_title(f'Visualización de Segmentos (PCA) - K={7}')
    ax[1].grid(True)

    plt.tight_layout()
    plt.savefig('outputs/kmeans_analysis.png')
    plt.show()
               


@training_bp.get("/training/kmeans")
def train_kmeans():
    """Entrenar modelo K-means para segmentación de clientes"""

    try:
        X_processed = preprocess_dataframe()
        # si se desea encontra el k optimo utilizar ModelStore.optimal_k (calculado arriba) 
        
        n_clusters = ModelStore.kmeans_params.get("n_clusters", 6) #Se trabaja 6 para el modelo

        kmeans = KMeans(
            n_clusters=n_clusters,
            init=ModelStore.kmeans_params.get("init", "k-means++"),
            n_init=ModelStore.kmeans_params.get("n_init", 10),
            max_iter=ModelStore.kmeans_params.get("max_iter", 500),
            random_state=ModelStore.kmeans_params.get("random_state", 42),
        )

        labels = kmeans.fit_predict(X_processed)
        ModelStore.kmeans_model = kmeans
        ModelStore.kmeans_labels = labels.tolist()
        # Añadir etiquetas al dataframe numérico
        if getattr(DataStore, 'df_numeric_cleaned', None) is not None:
            try:
                DataStore.df_numeric_cleaned["kmeans_cluster"] = labels
            except Exception:
                # Si hay desalineación, no romper
                pass

        # Calcular métricas
        silhouette = silhouette_score(X_processed, labels)
        davies_bouldin = davies_bouldin_score(X_processed, labels)
        calinski_harabasz = calinski_harabasz_score(X_processed, labels)



        return jsonify({
            "success": True,
            "message": "Modelo K-means entrenado exitosamente",
            "model_info": {
                "algorithm": "K-means",
                "n_clusters": int(n_clusters),
                "n_features": X_processed.shape[1],
                "n_samples": X_processed.shape[0],
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


@training_bp.get("/training/hierarchical")
def train_hierarchical():
    """Entrenar modelo Hierarchical Clustering para segmentación de clientes"""
  
    try:
        X_processed = preprocess_dataframe()
        # Obtener características para clustering
        
        # Normalizar características

        # Obtener parámetros del modelo
        n_clusters = ModelStore.hierarchical_params.get("n_clusters", 3)
        linkage = ModelStore.hierarchical_params.get("linkage", "ward")

        # Entrenar Hierarchical Clustering
        hierarchical = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage=linkage,
        )

        labels = hierarchical.fit_predict(X_processed)
        ModelStore.hierarchical_model = hierarchical
        ModelStore.hierarchical_labels = labels.tolist()

        # Calcular métricas
        silhouette = silhouette_score(X_processed, labels)
        davies_bouldin = davies_bouldin_score(X_processed, labels)
        calinski_harabasz = calinski_harabasz_score(X_processed, labels)

        # Agregar etiquetas al dataframe preprocesado
        if getattr(DataStore, 'df_numeric_cleaned', None) is not None:
            DataStore.df_numeric_cleaned["hierarchical_cluster"] = labels

        return jsonify({
            "success": True,
            "message": "Modelo Hierarchical Clustering entrenado exitosamente",
            "model_info": {
                "algorithm": "Hierarchical Clustering",
                "n_clusters": int(n_clusters),
                "linkage": linkage,
                "n_features": X_processed.shape[1],
                "n_samples": X_processed.shape[0],
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


@training_bp.get("/training/auto-k")
def train_auto_k():
    """Determina k óptimo usando silhouette y entrena K-Means."""

    try:
        X_processed = preprocess_dataframe()
        # Definir rango máximo de k en función de las muestras
        n_samples = X_processed.shape[0]
        if n_samples < 3:
            return jsonify({
                "error": "Insuficientes muestras para calcular silhouette (se requieren >= 3)."
            }), 400
        max_k = min(10, n_samples - 1)
        optimal_k = _find_optimal_k(X_processed, max_k=max_k)

        # Entrenar con k óptimo
        kmeans = KMeans(
            n_clusters=optimal_k,
            init=ModelStore.kmeans_params.get("init", "k-means++"),
            n_init=ModelStore.kmeans_params.get("n_init", 10),
            max_iter=ModelStore.kmeans_params.get("max_iter", 500),
            random_state=ModelStore.kmeans_params.get("random_state", 42),
        )
        labels = kmeans.fit_predict(X_processed)
        ModelStore.kmeans_model = kmeans
        ModelStore.kmeans_labels = labels.tolist()
        ModelStore.optimal_k = int(optimal_k)
        # Añadir etiquetas al dataframe numérico
        if getattr(DataStore, 'df_numeric_cleaned', None) is not None:
            try:
                DataStore.df_numeric_cleaned["kmeans_cluster"] = labels
            except Exception:
                pass

        silhouette = silhouette_score(X_processed, labels)
        davies_bouldin = davies_bouldin_score(X_processed, labels)
        calinski_harabasz = calinski_harabasz_score(X_processed, labels)

        return jsonify({
            "success": True,
            "message": f"Auto-K entrenado exitosamente con k={optimal_k}",
            "model_info": {
                "algorithm": "K-means (Auto-K)",
                "n_clusters": int(optimal_k),
                "n_features": X_processed.shape[1],
                "n_samples": X_processed.shape[0],
            },
            "metrics": {
                "inertia": float(kmeans.inertia_),
                "silhouette_score": float(silhouette),
                "davies_bouldin_score": float(davies_bouldin),
                "calinski_harabasz_score": float(calinski_harabasz),
            },
            "cluster_distribution": {
                str(i): int(np.sum(np.array(labels) == i))
                for i in range(int(optimal_k))
            }
        }), 200
    except ValueError as ve:
        return jsonify({
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Error al entrenar Auto-K",
            "detail": str(e)
        }), 500
 


@training_bp.get("/models/status")
def get_models_status():
    """Obtener estado de los modelos entrenados"""
    status = build_models_status()
    return jsonify(status), 200
