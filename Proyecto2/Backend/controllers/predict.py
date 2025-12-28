from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
from models import DataStore, ModelStore

predict_bp = Blueprint("predict", __name__)


@predict_bp.post("/predict/kmeans")
def predict_kmeans():
    """Asignar nuevos clientes a clusters usando K-means"""
    if ModelStore.kmeans_model is None:
        return jsonify({"error": "El modelo K-means no ha sido entrenado aún"}), 400

    try:
        data = request.get_json()
        
        if not data or "data" not in data:
            return jsonify({"error": "No se proporcionaron datos para predicción"}), 400

        # Convertir datos a DataFrame
        new_data = pd.DataFrame(data["data"])
        
        # Validar que tenga las columnas esperadas
        required_cols = [
            "frecuencia_compra",
            "monto_total_gastado",
            "monto_promedio_compra",
            "dias_desde_ultima_compra",
            "antiguedad_cliente_meses",
            "numero_productos_distintos",
            "canal_encoded",
        ]
        
        available_cols = [col for col in required_cols if col in new_data.columns]
        
        if len(available_cols) < 3:
            return jsonify({
                "error": "Datos insuficientes. Se requieren al menos 3 características"
            }), 400

        # Seleccionar y normalizar características
        features = new_data[available_cols].copy()
        
        if DataStore.scaler_for_models is not None:
            features_scaled = DataStore.scaler_for_models.transform(features)
        else:
            # Si no hay scaler guardado, normalizar manualmente
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)

        # Predecir clusters
        predictions = ModelStore.kmeans_model.predict(features_scaled)
        
        # Calcular distancias a centroides (para confianza)
        distances = ModelStore.kmeans_model.transform(features_scaled)
        min_distances = np.min(distances, axis=1)

        return jsonify({
            "success": True,
            "message": "Predicción completada con K-means",
            "predictions": {
                "clusters": predictions.tolist(),
                "distances_to_centroid": min_distances.tolist(),
                "n_samples": len(predictions),
            }
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error en predicción K-means",
            "detail": str(e)
        }), 500


@predict_bp.post("/predict/hierarchical")
def predict_hierarchical():
    """Información sobre clusters de Hierarchical Clustering"""
    if ModelStore.hierarchical_model is None:
        return jsonify({
            "error": "El modelo Hierarchical Clustering no ha sido entrenado aún"
        }), 400

    try:
        # Hierarchical Clustering no puede predecir datos nuevos directamente
        # Solo podemos obtener información sobre los clusters entrenados
        
        labels = ModelStore.hierarchical_labels
        n_clusters = ModelStore.hierarchical_params.get("n_clusters", 3)

        cluster_info = {}
        for i in range(n_clusters):
            count = sum(1 for label in labels if label == i)
            cluster_info[str(i)] = {
                "size": count,
                "percentage": round((count / len(labels)) * 100, 2)
            }

        return jsonify({
            "success": True,
            "message": "Información de clusters Hierarchical Clustering",
            "hierarchical_info": {
                "algorithm": "Hierarchical Clustering",
                "n_clusters": n_clusters,
                "linkage": ModelStore.hierarchical_params.get("linkage", "ward"),
                "total_samples": len(labels),
                "clusters": cluster_info,
            }
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error obteniendo información de Hierarchical Clustering",
            "detail": str(e)
        }), 500


@predict_bp.get("/results/kmeans")
def get_kmeans_results():
    """Obtener resultados completos de K-means"""
    if ModelStore.kmeans_model is None or DataStore.df_preprocessed is None:
        return jsonify({
            "error": "El modelo no ha sido entrenado o los datos no han sido cargados"
        }), 400

    try:
        df_with_clusters = DataStore.df_preprocessed.copy()
        df_with_clusters["cluster"] = ModelStore.kmeans_labels

        # Estadísticas por cluster
        cluster_stats = {}
        for cluster_id in set(ModelStore.kmeans_labels):
            cluster_data = df_with_clusters[df_with_clusters["cluster"] == cluster_id]
            
            stats = {}
            for col in cluster_data.select_dtypes(include=['number']).columns:
                if col != "cliente_id" and col != "cluster":
                    stats[col] = {
                        "mean": float(cluster_data[col].mean()),
                        "median": float(cluster_data[col].median()),
                        "std": float(cluster_data[col].std()),
                        "min": float(cluster_data[col].min()),
                        "max": float(cluster_data[col].max()),
                    }
            
            cluster_stats[f"cluster_{cluster_id}"] = {
                "size": len(cluster_data),
                "statistics": stats,
            }

        return jsonify({
            "success": True,
            "algorithm": "K-means",
            "n_clusters": ModelStore.kmeans_params.get("n_clusters"),
            "total_clients": len(df_with_clusters),
            "cluster_statistics": cluster_stats,
            "sample_data": df_with_clusters.head(20).to_dict(orient="records"),
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error obteniendo resultados de K-means",
            "detail": str(e)
        }), 500


@predict_bp.get("/results/hierarchical")
def get_hierarchical_results():
    """Obtener resultados completos de Hierarchical Clustering"""
    if ModelStore.hierarchical_model is None or DataStore.df_preprocessed is None:
        return jsonify({
            "error": "El modelo no ha sido entrenado o los datos no han sido cargados"
        }), 400

    try:
        df_with_clusters = DataStore.df_preprocessed.copy()
        df_with_clusters["cluster"] = ModelStore.hierarchical_labels

        # Estadísticas por cluster
        cluster_stats = {}
        for cluster_id in set(ModelStore.hierarchical_labels):
            cluster_data = df_with_clusters[df_with_clusters["cluster"] == cluster_id]
            
            stats = {}
            for col in cluster_data.select_dtypes(include=['number']).columns:
                if col != "cliente_id" and col != "cluster":
                    stats[col] = {
                        "mean": float(cluster_data[col].mean()),
                        "median": float(cluster_data[col].median()),
                        "std": float(cluster_data[col].std()),
                        "min": float(cluster_data[col].min()),
                        "max": float(cluster_data[col].max()),
                    }
            
            cluster_stats[f"cluster_{cluster_id}"] = {
                "size": len(cluster_data),
                "statistics": stats,
            }

        return jsonify({
            "success": True,
            "algorithm": "Hierarchical Clustering",
            "linkage": ModelStore.hierarchical_params.get("linkage"),
            "n_clusters": ModelStore.hierarchical_params.get("n_clusters"),
            "total_clients": len(df_with_clusters),
            "cluster_statistics": cluster_stats,
            "sample_data": df_with_clusters.head(20).to_dict(orient="records"),
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error obteniendo resultados de Hierarchical Clustering",
            "detail": str(e)
        }), 500


@predict_bp.get("/results/comparison")
def get_comparison():
    """Comparar resultados de ambos modelos"""
    if (ModelStore.kmeans_model is None or 
        ModelStore.hierarchical_model is None or 
        DataStore.df_preprocessed is None):
        return jsonify({
            "error": "Ambos modelos deben estar entrenados para hacer una comparación"
        }), 400

    try:
        df_comparison = DataStore.df_preprocessed.copy()
        df_comparison["kmeans_cluster"] = ModelStore.kmeans_labels
        df_comparison["hierarchical_cluster"] = ModelStore.hierarchical_labels

        # Matriz de confusión
        confusion_matrix = pd.crosstab(
            df_comparison["kmeans_cluster"],
            df_comparison["hierarchical_cluster"],
            margins=True
        )

        return jsonify({
            "success": True,
            "message": "Comparación de modelos",
            "kmeans_clusters": ModelStore.kmeans_params.get("n_clusters"),
            "hierarchical_clusters": ModelStore.hierarchical_params.get("n_clusters"),
            "total_samples": len(df_comparison),
            "agreement_rate": float(
                sum(df_comparison["kmeans_cluster"] == df_comparison["hierarchical_cluster"]) / len(df_comparison)
            ),
            "confusion_matrix": confusion_matrix.to_dict(),
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error en comparación de modelos",
            "detail": str(e)
        }), 500
