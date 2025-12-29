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

training_bp = Blueprint("training", __name__)


def _find_optimal_k(data: np.ndarray, max_k: int = 10) -> int: 
    # Metodo del codo
    inertias = []
    silhouette_scores = []
    k_range = range(1, max_k + 1)
    for k in k_range:
        kmeans = KMeans(
            n_clusters=k,
            init="k-means++",
            n_init=10,
            random_state=42,
            max_iter=500, # editable
        )
        kmeans.fit(data)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(data, kmeans.labels_))
    # Usar silhouette score para encontrar el óptimo
    optimal_k = list(k_range)[np.argmax(silhouette_scores)]
    ModelStore.optimal_k = optimal_k
    return optimal_k

def preprocess_dataframe()->np.ndarray:
    num_cols = [
            "frecuencia_compra",
            "monto_total_gastado",
            "monto_promedio_compra",
            "dias_desde_ultima_compra",
            "antiguedad_cliente_meses",
            "numero_productos_distintos"

    ]    
    cat_cols = ['canal_principal', 'producto_categoria']
    DataStore.df_cleaned = DataStore.df_cleaned.drop(columns=["producto_categoria", "canal_principal"])

    if getattr(DataStore, 'df_cleaned', None) is None:
        return jsonify({"error": "Primero ejecute la limpieza de datos (/clean)"}), 400
    
    preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_cols),
        # ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
    ])

    X_processed = preprocessor.fit_transform(DataStore.df_cleaned)
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
    X_processed = preprocess_dataframe()
    """Entrenar modelo K-means para segmentación de clientes"""
    if DataStore.df_cleaned is None:
        return jsonify({"error": "Los datos no han sido preprocesados aún"}), 400

    try:
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
    X_processed = preprocess_dataframe()

    """Entrenar modelo Hierarchical Clustering para segmentación de clientes"""
  
    try:
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
        DataStore.df_cleaned["hierarchical_cluster"] = labels

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
