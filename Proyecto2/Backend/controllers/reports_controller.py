from flask import Blueprint, jsonify, request, send_file
import os

from reports.segment_profiles import compute_numeric_profiles
from reports.segment_patterns import compute_text_patterns
from reports.export_report import export_all_reports
from reports.segment_descriptions import build_segment_descriptions
from reports.sentiment_report import compute_sentiment_report

reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/reports/numeric-profile")
def get_numeric_profile():
    cluster_col = request.args.get("cluster_col")
    try:
        # No crear subcarpetas en llamadas del frontend
        result = compute_numeric_profiles(cluster_col=cluster_col, use_subdir=False)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@reports_bp.get("/reports/text-patterns")
def get_text_patterns():
    top_n = request.args.get("top_n", default=12, type=int)
    try:
        # No crear subcarpetas en llamadas del frontend
        result = compute_text_patterns(top_n=top_n, use_subdir=False)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@reports_bp.get("/reports/sentiment")
def get_sentiment_report():
    """Obtiene reporte de sentimientos independiente del clustering.

    No crea subcarpetas (pensado para llamadas del frontend).
    """
    try:
        result = compute_sentiment_report(use_subdir=False)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@reports_bp.get("/reports/descriptions")
def get_descriptions():
    cluster_col = request.args.get("cluster_col")
    top_n = request.args.get("top_n", default=12, type=int)
    z_high = request.args.get("z_high", default=0.7, type=float)
    z_low = request.args.get("z_low", default=-0.7, type=float)
    try:
        # No crear subcarpetas en llamadas del frontend
        numeric = compute_numeric_profiles(cluster_col=cluster_col, use_subdir=False)
        text = compute_text_patterns(top_n=top_n, use_subdir=False)
        descriptions = build_segment_descriptions(numeric, text, z_high=z_high, z_low=z_low)
        return jsonify({"success": True, "data": descriptions}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@reports_bp.post("/reports/export")
def post_export():
    cluster_col = request.json.get("cluster_col") if request.is_json else None
    top_n = request.json.get("top_n", 12) if request.is_json else 12
    z_high = request.json.get("z_high", 0.7) if request.is_json else 0.7
    z_low = request.json.get("z_low", -0.7) if request.is_json else -0.7
    try:
        result = export_all_reports(cluster_col=cluster_col, top_n=top_n, z_high=z_high, z_low=z_low)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


    


@reports_bp.get("/reports/file")
def get_report_file():
    """Sirve archivos generados en la carpeta de reports/exports de forma segura.

    Parámetro query `path`: ruta absoluta a un archivo dentro de reports/exports.
    """
    path = request.args.get("path")
    if not path:
        return jsonify({"success": False, "error": "Missing 'path' query parameter"}), 400

    # Base segura: Backend/reports
    base_reports = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    real_path = os.path.realpath(path)
    if not real_path.startswith(base_reports):
        return jsonify({"success": False, "error": "Access denied"}), 403
    if not os.path.isfile(real_path):
        return jsonify({"success": False, "error": "File not found"}), 404

    try:
        resp = send_file(real_path)
        # Deshabilitar caché para evitar 304 y mostrar archivos antiguos o incompletos
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
