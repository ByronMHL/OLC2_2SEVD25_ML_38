from flask import Blueprint, jsonify, request
from models import ModelStore

hyper_bp = Blueprint("hyperparameters", __name__)


@hyper_bp.get("/hyperparameters/kmeans")
def get_kmeans_params():
    """Obtener parámetros actuales de K-means"""
    return jsonify({
        "algorithm": "K-means",
        "parameters": ModelStore.kmeans_params,
    }), 200


@hyper_bp.post("/hyperparameters/kmeans")
def set_kmeans_params():
    """Actualizar parámetros de K-means"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron parámetros"}), 400

        # Validar y actualizar parámetros
        if "n_clusters" in data:
            n_clusters = int(data["n_clusters"])
            if n_clusters < 2:
                return jsonify({"error": "n_clusters debe ser >= 2"}), 400
            ModelStore.kmeans_params["n_clusters"] = n_clusters

        if "init" in data:
            init_method = data["init"]
            if init_method not in ["k-means++", "random"]:
                return jsonify({"error": "init debe ser 'k-means++' o 'random'"}), 400
            ModelStore.kmeans_params["init"] = init_method

        if "n_init" in data:
            n_init = int(data["n_init"])
            if n_init < 1:
                return jsonify({"error": "n_init debe ser >= 1"}), 400
            ModelStore.kmeans_params["n_init"] = n_init

        if "max_iter" in data:
            max_iter = int(data["max_iter"])
            if max_iter < 1:
                return jsonify({"error": "max_iter debe ser >= 1"}), 400
            ModelStore.kmeans_params["max_iter"] = max_iter

        if "random_state" in data:
            random_state = int(data["random_state"])
            if random_state < 0:
                return jsonify({"error": "random_state debe ser >= 0"}), 400
            ModelStore.kmeans_params["random_state"] = random_state

        return jsonify({
            "success": True,
            "message": "Parámetros de K-means actualizados",
            "parameters": ModelStore.kmeans_params,
        }), 200

    except ValueError as e:
        return jsonify({
            "error": "Error en los tipos de datos",
            "detail": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Error al actualizar parámetros",
            "detail": str(e)
        }), 500


@hyper_bp.get("/hyperparameters/hierarchical")
def get_hierarchical_params():
    """Obtener parámetros actuales de Hierarchical Clustering"""
    return jsonify({
        "algorithm": "Hierarchical Clustering",
        "parameters": ModelStore.hierarchical_params,
    }), 200


@hyper_bp.post("/hyperparameters/hierarchical")
def set_hierarchical_params():
    """Actualizar parámetros de Hierarchical Clustering"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron parámetros"}), 400

        # Validar y actualizar parámetros
        if "n_clusters" in data:
            n_clusters = int(data["n_clusters"])
            if n_clusters < 2:
                return jsonify({"error": "n_clusters debe ser >= 2"}), 400
            ModelStore.hierarchical_params["n_clusters"] = n_clusters

        if "linkage" in data:
            linkage = data["linkage"]
            if linkage not in ["ward", "complete", "average", "single"]:
                return jsonify({
                    "error": "linkage debe ser 'ward', 'complete', 'average' o 'single'"
                }), 400
            ModelStore.hierarchical_params["linkage"] = linkage

        return jsonify({
            "success": True,
            "message": "Parámetros de Hierarchical Clustering actualizados",
            "parameters": ModelStore.hierarchical_params,
        }), 200

    except ValueError as e:
        return jsonify({
            "error": "Error en los tipos de datos",
            "detail": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Error al actualizar parámetros",
            "detail": str(e)
        }), 500


@hyper_bp.get("/hyperparameters/all")
def get_all_params():
    """Obtener todos los parámetros de configuración"""
    return jsonify({
        "kmeans": ModelStore.kmeans_params,
        "hierarchical": ModelStore.hierarchical_params,
        "notes": {
            "kmeans_init": "k-means++ (recomendado) o random",
            "kmeans_n_init": "Número de inicializaciones (mayor = más tiempo pero mejor convergencia)",
            "hierarchical_linkage": "ward (recomendado), complete, average, o single",
        }
    }), 200
