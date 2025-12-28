import os
from flask import Blueprint, jsonify, request
import pandas as pd
from models import DataStore

upload_bp = Blueprint("upload", __name__)


# def _paths():
#     """Obtener ruta del directorio de datos"""
#     backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
#     workspace_root = os.path.abspath(os.path.join(backend_dir, os.pardir))
#     data_raw_dir = os.path.join(workspace_root, "data", "raw")
#     os.makedirs(data_raw_dir, exist_ok=True)
#     return data_raw_dir


# Columnas esperadas según especificación
REQUIRED_COLUMNS = {
    "cliente_id",
    "frecuencia_compra",
    "monto_total_gastado",
    "monto_promedio_compra",
    "dias_desde_ultima_compra",
    "antiguedad_cliente_meses",
    "canal_principal",
    "numero_productos_distintos",
    "reseña_id",
    "texto_reseña",
    "fecha_reseña",
    "producto_categoria",
}


@upload_bp.get("/health")
def health():
    
    return jsonify({"status": "ok"}),200


@upload_bp.post("/upload")
def upload_csv():
    """Carga masiva de archivo CSV"""
    if "file" not in request.files:
        return jsonify({"error": "No se encontró el campo 'file' en la solicitud"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    # Solo CSV por ahora
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Formato inválido. Solo se aceptan archivos .csv"}), 400

    # Intentar leer CSV con pandas para validar estructura
    DataStore.df_raw = None
    try:
        df = pd.read_csv(file)
        DataStore.df_raw = df
    except Exception as e:
        return jsonify({"error": "No se pudo leer el CSV", "detail": str(e)}), 400

    #Checking Columns
    received_columns = set(df.columns.str.strip())
    missing = list(sorted(REQUIRED_COLUMNS - received_columns))
    extra = list(sorted(received_columns - REQUIRED_COLUMNS))

    if missing:
        return jsonify({
            "error": "Columnas faltantes",
            "missing_columns": missing,
        }), 400

    response = {
        "success": True,
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        "message": "Archivo cargado exitosamente",
    }

    if extra:
        response["extra_columns"] = extra

    return jsonify(response), 200


@upload_bp.get("/raw-data")
def get_raw_data():
    """Obtener vista previa de datos cargados"""
    if DataStore.df_raw is None:
        return jsonify({"error": "No se ha cargado ningún archivo"}), 400

    return jsonify({
        "rows": len(DataStore.df_raw),
        "columns": list(DataStore.df_raw.columns),
        "data_types": DataStore.df_raw.dtypes.to_dict(),
        "head": DataStore.df_raw.head(5).to_dict(orient="records"),
    }), 200
