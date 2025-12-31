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

    # Intentar leer CSV con pandas para validar estructura (UTF-8 por defecto)
    DataStore.df_raw = None
    encoding_param = (request.args.get("encoding") or request.form.get("encoding") or "utf-8").lower()
    encoding_used = encoding_param
    try:
        df = pd.read_csv(file, encoding=encoding_param)
        DataStore.df_raw = df
    except UnicodeDecodeError:
        # Fallback a UTF-8 con BOM si viene con cabecera BOM y se especificó utf-8
        if encoding_param == "utf-8":
            try:
                file.stream.seek(0)
                df = pd.read_csv(file, encoding="utf-8-sig")
                DataStore.df_raw = df
                encoding_used = "utf-8-sig"
            except Exception as e:
                return jsonify({"error": "No se pudo leer el CSV (utf-8/utf-8-sig)", "detail": str(e)}), 400
        else:
            return jsonify({"error": f"Error de decodificación con encoding '{encoding_param}'"}), 400
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
        "encoding_used": encoding_used,
    }

    if extra:
        response["extra_columns"] = extra

    return jsonify(response), 200


@upload_bp.get("/raw-data")
def get_raw_data():
    """Obtener vista previa de datos cargados"""
    if DataStore.df_raw is None:
        return jsonify({"error": "No se ha cargado ningún archivo"}), 400

    # Asegurar que los tipos sean serializables (convertir a str)
    dtypes_dict = {k: str(v) for k, v in DataStore.df_raw.dtypes.to_dict().items()}

    return jsonify({
        "rows": len(DataStore.df_raw),
        "columns": list(DataStore.df_raw.columns),
        "data_types": dtypes_dict,
        "head": DataStore.df_raw.head(5).to_dict(orient="records"),
    }), 200
