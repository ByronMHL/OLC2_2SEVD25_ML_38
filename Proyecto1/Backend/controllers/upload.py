import os
from datetime import datetime
from flask import Blueprint, jsonify, request
import pandas as pd


upload_bp = Blueprint("upload", __name__)


def _paths():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    workspace_root = os.path.abspath(os.path.join(backend_dir, os.pardir))
    data_raw_dir = os.path.join(workspace_root, "data", "raw")
    os.makedirs(data_raw_dir, exist_ok=True)
    return data_raw_dir


# Columnas esperadas según README
REQUIRED_COLUMNS = {
    "promedio_actual",
    "asistencia_clases",
    "tareas_entregadas",
    "participacion_clase",
    "horas_estudio",
    "promedio_evaluaciones",
    "cursos_reprobados",
    "actividades_extracurriculares",
    "reportes_disciplinarios",
    "riesgo",
}


@upload_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "studentguard-backend"})


@upload_bp.post("/upload")
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No se encontró el campo 'file' en la solicitud"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    # Solo CSV por ahora
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Formato inválido. Solo se aceptan archivos .csv"}), 400

    # Verificar si un archivo con el mismo nombre ya fue subido previamente
    data_raw_dir = _paths()
    safe_name = os.path.basename(file.filename)
    try:
        existing = [fname for fname in os.listdir(data_raw_dir) if fname.endswith(f"_{safe_name}")]
    except Exception:
        existing = []

    if existing:
        return jsonify({
            "error": "Archivo ya fue subido previamente",
            "filename": safe_name,
            "existing_entries": existing,
        }), 409

    # Intentar leer CSV con pandas para validar estructura
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return jsonify({"error": "No se pudo leer el CSV", "detail": str(e)}), 400

    received_columns = set(df.columns.str.strip())
    missing = list(sorted(REQUIRED_COLUMNS - received_columns))
    extra = list(sorted(received_columns - REQUIRED_COLUMNS))

    if missing:
        return jsonify({
            "error": "Columnas requeridas faltantes",
            "missing": missing,
            "required": sorted(list(REQUIRED_COLUMNS)),
        }), 400

    # Se guarda el archivo con un timestamp para evitar colisiones
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    out_name = f"upload_{timestamp}_{safe_name}"
    out_path = os.path.join(data_raw_dir, out_name)
    try:
        df.to_csv(out_path, index=False)
    except Exception:
        file.stream.seek(0)
        with open(out_path, "wb") as f:
            f.write(file.read())

    return jsonify({
        "message": "Archivo CSV recibido y validado",
        "saved_to": out_path,
        "rows": int(df.shape[0]),
        "columns": sorted(list(received_columns)),
        "extra_columns": extra,
    }), 200
