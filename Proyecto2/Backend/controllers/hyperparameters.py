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
        "text_kmeans": ModelStore.text_kmeans_params,
        "notes": {
            "kmeans_init": "k-means++ (recomendado) o random",
            "kmeans_n_init": "Número de inicializaciones (mayor = más tiempo pero mejor convergencia)",
            "hierarchical_linkage": "ward (recomendado), complete, average, o single",
            "text_kmeans": "Incluye parámetros de KMeans y TF-IDF (max_features, min_df, max_df)",
        }
    }), 200


@hyper_bp.get("/hyperparameters/text_kmeans")
def get_text_kmeans_params():
    """Obtener parámetros actuales para clustering textual (TF-IDF + KMeans)"""
    return jsonify({
        "algorithm": "K-means (Text TF-IDF)",
        "parameters": ModelStore.text_kmeans_params,
    }), 200


@hyper_bp.post("/hyperparameters/text_kmeans")
def set_text_kmeans_params():
    """Actualizar parámetros para clustering textual (TF-IDF + KMeans)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron parámetros"}), 400

        # Parámetros de KMeans
        if "n_clusters" in data:
            n_clusters = int(data["n_clusters"])
            if n_clusters < 2:
                return jsonify({"error": "n_clusters debe ser >= 2"}), 400
            ModelStore.text_kmeans_params["n_clusters"] = n_clusters

        if "init" in data:
            init_method = data["init"]
            if init_method not in ["k-means++", "random"]:
                return jsonify({"error": "init debe ser 'k-means++' o 'random'"}), 400
            ModelStore.text_kmeans_params["init"] = init_method

        if "n_init" in data:
            n_init = int(data["n_init"])
            if n_init < 1:
                return jsonify({"error": "n_init debe ser >= 1"}), 400
            ModelStore.text_kmeans_params["n_init"] = n_init

        if "max_iter" in data:
            max_iter = int(data["max_iter"])
            if max_iter < 1:
                return jsonify({"error": "max_iter debe ser >= 1"}), 400
            ModelStore.text_kmeans_params["max_iter"] = max_iter

        if "random_state" in data:
            random_state = int(data["random_state"])
            if random_state < 0:
                return jsonify({"error": "random_state debe ser >= 0"}), 400
            ModelStore.text_kmeans_params["random_state"] = random_state

        # Parámetros de TF-IDF
        if "tfidf_max_features" in data:
            mf = int(data["tfidf_max_features"])
            if mf < 100:
                return jsonify({"error": "tfidf_max_features debe ser >= 100"}), 400
            ModelStore.text_kmeans_params["tfidf_max_features"] = mf

        if "tfidf_min_df" in data:
            min_df = data["tfidf_min_df"]
            # Permitir int >=1 o float en [0,1]
            if isinstance(min_df, float):
                if not (0.0 <= min_df <= 1.0):
                    return jsonify({"error": "tfidf_min_df (float) debe estar en [0,1]"}), 400
            else:
                min_df = int(min_df)
                if min_df < 1:
                    return jsonify({"error": "tfidf_min_df (int) debe ser >= 1"}), 400
            ModelStore.text_kmeans_params["tfidf_min_df"] = min_df

        if "tfidf_max_df" in data:
            max_df = float(data["tfidf_max_df"])
            if not (0.0 < max_df <= 1.0):
                return jsonify({"error": "tfidf_max_df debe estar en (0,1]"}), 400
            ModelStore.text_kmeans_params["tfidf_max_df"] = max_df

        # Nuevos parámetros TF-IDF
        if "ngram_range" in data:
            ngr = data["ngram_range"]
            # Espera lista/tupla de dos enteros [a,b] con 1<=a<=b
            if not isinstance(ngr, (list, tuple)) or len(ngr) != 2:
                return jsonify({"error": "ngram_range debe ser [min_n, max_n]"}), 400
            try:
                a = int(ngr[0]); b = int(ngr[1])
            except Exception:
                return jsonify({"error": "ngram_range debe contener enteros"}), 400
            if a < 1 or b < a:
                return jsonify({"error": "ngram_range inválido: se requiere 1 <= min_n <= max_n"}), 400
            ModelStore.text_kmeans_params["ngram_range"] = (a, b)

        if "sublinear_tf" in data:
            # Acepta booleano literal; si viene string, interpretar 'true'/'false'
            val = data["sublinear_tf"]
            if isinstance(val, str):
                val_l = val.strip().lower()
                if val_l in ["true", "1", "yes", "y", "si", "sí"]:
                    val = True
                elif val_l in ["false", "0", "no", "n"]:
                    val = False
                else:
                    return jsonify({"error": "sublinear_tf debe ser booleano"}), 400
            elif not isinstance(val, bool):
                return jsonify({"error": "sublinear_tf debe ser booleano"}), 400
            ModelStore.text_kmeans_params["sublinear_tf"] = bool(val)

        if "norm" in data:
            norm = data["norm"]
            # Permitir 'l2', 'l1' o None/'none'
            if norm is None:
                ModelStore.text_kmeans_params["norm"] = None
            else:
                norm_s = str(norm).lower()
                if norm_s in ["none", "null"]:
                    ModelStore.text_kmeans_params["norm"] = None
                elif norm_s in ["l1", "l2"]:
                    ModelStore.text_kmeans_params["norm"] = norm_s
                else:
                    return jsonify({"error": "norm debe ser 'l1', 'l2' o null"}), 400

        return jsonify({
            "success": True,
            "message": "Parámetros de clustering textual actualizados",
            "parameters": ModelStore.text_kmeans_params,
        }), 200

    except ValueError as e:
        return jsonify({
            "error": "Error en los tipos de datos",
            "detail": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Error al actualizar parámetros de texto",
            "detail": str(e)
        }), 500
