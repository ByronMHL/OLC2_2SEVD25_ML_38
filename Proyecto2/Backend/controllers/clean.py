from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
import re
from models import DataStore

clean_bp = Blueprint("clean", __name__)


def _perform_numeric_clean(df_raw: pd.DataFrame) -> dict:
    """Ejecuta la limpieza numérica y retorna dict con df y stats."""
    required_drop = ["cliente_id", "reseña_id", "fecha_reseña", "texto_reseña"]
    present_drop = [c for c in required_drop if c in df_raw.columns]
    df_num = df_raw.drop(columns=present_drop)
    df_num = df_num.drop_duplicates()

    # Conversión numérica segura
    numeric_cols = [
        "frecuencia_compra",
        "monto_total_gastado",
        "monto_promedio_compra",
        "dias_desde_ultima_compra",
        "antiguedad_cliente_meses",
        "numero_productos_distintos",
    ]
    for col in numeric_cols:
        if col in df_num.columns:
            dtype = 'float64' if 'monto' in col else 'int32'
            df_num[col] = pd.to_numeric(df_num[col], errors='coerce').fillna(0).astype(dtype)

    # Imputación de ceros por mediana/media
    if "frecuencia_compra" in df_num.columns:
        df_num.loc[df_num['frecuencia_compra'] == 0, 'frecuencia_compra'] = df_num["frecuencia_compra"].median()
    if "dias_desde_ultima_compra" in df_num.columns:
        df_num.loc[df_num['dias_desde_ultima_compra'] == 0, 'dias_desde_ultima_compra'] = df_num["dias_desde_ultima_compra"].median()
    if "antiguedad_cliente_meses" in df_num.columns:
        df_num.loc[df_num['antiguedad_cliente_meses'] == 0, 'antiguedad_cliente_meses'] = df_num["antiguedad_cliente_meses"].median()
    if "numero_productos_distintos" in df_num.columns:
        df_num.loc[df_num['numero_productos_distintos'] == 0, 'numero_productos_distintos'] = df_num["numero_productos_distintos"].median()

    if "monto_total_gastado" in df_num.columns:
        df_num.loc[df_num['monto_total_gastado'] == 0, 'monto_total_gastado'] = df_num["monto_total_gastado"].mean()
    if "monto_promedio_compra" in df_num.columns:
        df_num.loc[df_num['monto_promedio_compra'] == 0, 'monto_promedio_compra'] = df_num["monto_promedio_compra"].mean()

    # Categóricas conocidas
    if "canal_principal" in df_num.columns:
        df_num["canal_principal"] = (df_num["canal_principal"].astype("string").fillna("Desconocido"))
    if "producto_categoria" in df_num.columns:
        df_num["producto_categoria"] = (df_num["producto_categoria"].astype("string").fillna("Desconocido"))

    return {
        "df": df_num,
        "stats": {
            "final_rows": len(df_num),
            "columns": list(df_num.columns),
        }
    }


def _perform_text_clean(df_raw: pd.DataFrame) -> dict:
    """Ejecuta limpieza textual y retorna dict con df y stats."""
    if "texto_reseña" not in df_raw.columns:
        raise ValueError("La columna 'texto_reseña' no existe en los datos")

    df_text = df_raw[["texto_reseña"]].copy()
    df_text["texto_reseña"] = df_text["texto_reseña"].astype("string").fillna("")
    df_text["texto_lower"] = df_text["texto_reseña"].str.lower()
    df_text["texto_sin_signos"] = df_text["texto_lower"].apply(lambda s: re.sub(r"[^\w\s]", " ", s))
    df_text["tokens"] = df_text["texto_sin_signos"].apply(lambda s: [t for t in re.split(r"\s+", s.strip()) if t])
    df_text["texto_limpio"] = df_text["tokens"].apply(lambda toks: " ".join(toks))

    return {
        "df": df_text,
        "stats": {
            "rows": len(df_text),
            "empty_text_count": int((df_text["texto_reseña"] == "").sum()),
        },
        "preview": df_text.head(10).to_dict(orient="records"),
    }

@clean_bp.get("/clean")
def clean_data():
    """Limpieza para clustering numérico (no incluye procesamiento de texto)."""
    if DataStore.df_raw is None:
        return jsonify({"error": "No se ha cargado ningún archivo .csv"}), 400

    try:
        # Ejecutar limpieza numérica reutilizando helper
        num_res = _perform_numeric_clean(DataStore.df_raw)
        DataStore.df_numeric_cleaned = num_res["df"].copy()
        DataStore.df_cleaned = DataStore.df_numeric_cleaned  # compatibilidad



 
        return jsonify({
            "success": True,
            "message": "Limpieza numérica completada exitosamente",
            "statistics": {
                "initial_rows": len(DataStore.df_raw),
                **num_res["stats"],
            },
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error durante la limpieza",
            "detail": str(e)
        }), 500


@clean_bp.get("/cleaned-data")
def get_cleaned_data():
    """Obtener vista previa de datos limpios para clustering numérico"""
    if DataStore.df_numeric_cleaned is None:
        return jsonify({"error": "No se han limpiado datos numéricos aún"}), 400

    return jsonify({
        "rows": len(DataStore.df_numeric_cleaned),
        "columns": list(DataStore.df_numeric_cleaned.columns),
        "head": DataStore.df_numeric_cleaned.head(10).to_dict(orient="records"),
        "statistics": {
            "numeric_stats": DataStore.df_numeric_cleaned.describe().to_dict(),
            "null_counts": DataStore.df_numeric_cleaned.isnull().sum().to_dict(),
        }
    }), 200


@clean_bp.get("/clean-text")
def clean_text_data():
    """Limpieza para clustering textual: lowercase, quitar signos, tokenización básica sobre 'texto_reseña'."""
    if DataStore.df_raw is None:
        return jsonify({"error": "No se ha cargado ningún archivo .csv"}), 400

    if "texto_reseña" not in DataStore.df_raw.columns:
        return jsonify({"error": "La columna 'texto_reseña' no existe en los datos"}), 400

    try:
        text_res = _perform_text_clean(DataStore.df_raw)
        DataStore.df_text_cleaned = text_res["df"]

        return jsonify({
            "success": True,
            "message": "Limpieza textual completada exitosamente",
            "statistics": text_res["stats"],
            "preview": text_res["preview"],
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Error durante la limpieza textual",
            "detail": str(e)
        }), 500


@clean_bp.get("/text/preview")
def preview_text_tokens():
    """Listado de frecuencias de tokens desde df_text_cleaned."""
    if DataStore.df_text_cleaned is None:
        return jsonify({"error": "Primero ejecute la limpieza textual (/clean-text)"}), 400

    try:
        top_n = int(request.args.get("top", 50))
        # Concatenar todas las listas de tokens
        tokens_series = DataStore.df_text_cleaned["tokens"]
        all_tokens = []
        for toks in tokens_series:
            if isinstance(toks, list):
                all_tokens.extend(toks)
        # Contar frecuencias
        from collections import Counter
        counts = Counter(all_tokens)
        most_common = counts.most_common(top_n)
        return jsonify({
            "success": True,
            "top": top_n,
            "vocab_size": len(counts),
            "most_common": [{"token": t, "count": c} for t, c in most_common]
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Error al generar preview textual",
            "detail": str(e)
        }), 500


@clean_bp.get("/clean-all")
def clean_all():
    """Ejecuta limpieza numérica y textual en una sola llamada."""
    if DataStore.df_raw is None:
        return jsonify({"error": "No se ha cargado ningún archivo .csv"}), 400

    try:
        # Numérico
        num_res = _perform_numeric_clean(DataStore.df_raw)
        DataStore.df_numeric_cleaned = num_res["df"].copy()
        DataStore.df_cleaned = DataStore.df_numeric_cleaned  # compatibilidad

        # Textual (si existe columna)
        text_summary = None
        try:
            text_res = _perform_text_clean(DataStore.df_raw)
            DataStore.df_text_cleaned = text_res["df"]
            text_summary = {
                "statistics": text_res["stats"],
                "preview": text_res["preview"],
            }
        except ValueError:
            # Si no existe texto_reseña, retornar nota sin error
            text_summary = {
                "note": "Columna 'texto_reseña' no encontrada; se omitió limpieza textual."
            }

        return jsonify({
            "success": True,
            "message": "Limpieza numérica y textual completadas",
            "numeric": {
                "statistics": {
                    "initial_rows": len(DataStore.df_raw),
                    **num_res["stats"],
                }
            },
            "textual": text_summary,
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Error durante la limpieza combinada",
            "detail": str(e)
        }), 500
