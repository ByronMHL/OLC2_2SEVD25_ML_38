from models import ModelStore


def build_models_status():
    """Construye el diccionario de estado de todos los modelos entrenados."""
    return {
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
        "text_kmeans": {
            "trained": ModelStore.text_kmeans_model is not None,
            "n_clusters": ModelStore.text_kmeans_params.get("n_clusters"),
            "labels_count": len(ModelStore.text_kmeans_labels) if ModelStore.text_kmeans_labels else 0,
        },
    }
