from flask import Blueprint, jsonify
import pandas as pd
import numpy as np
from models import DataStore

clean_bp = Blueprint("clean", __name__)


@clean_bp.get("/clean")
def clean_data():
    """Limpieza y preprocesamiento de datos de clientes y reseñas"""
    if DataStore.df_raw is None:
        return jsonify({"error": "No se ha cargado ningún archivo .csv"}), 400

    try:

        # ===== LIMPIEZA DE DATOS =====
        DataStore.df_cleaned = DataStore.df_raw.drop(columns=["cliente_id", "reseña_id", "fecha_reseña","texto_reseña"])
        DataStore.df_cleaned = DataStore.df_cleaned.drop_duplicates()


        
        DataStore.df_cleaned["frecuencia_compra"] = pd.to_numeric(DataStore.df_cleaned["frecuencia_compra"], errors='coerce').fillna(0).astype('int32') 
        DataStore.df_cleaned["monto_total_gastado"] = pd.to_numeric(DataStore.df_cleaned["monto_total_gastado"], errors='coerce').fillna(0).astype('float64') 
        DataStore.df_cleaned["monto_promedio_compra"] = pd.to_numeric(DataStore.df_cleaned["monto_promedio_compra"], errors='coerce').fillna(0).astype('float64') 
        DataStore.df_cleaned["dias_desde_ultima_compra"] = pd.to_numeric(DataStore.df_cleaned["dias_desde_ultima_compra"], errors='coerce').fillna(0).astype('int32') 
        DataStore.df_cleaned["antiguedad_cliente_meses"] = pd.to_numeric(DataStore.df_cleaned["antiguedad_cliente_meses"], errors='coerce').fillna(0).astype('int32') 
        DataStore.df_cleaned["numero_productos_distintos"] = pd.to_numeric(DataStore.df_cleaned["numero_productos_distintos"], errors='coerce').fillna(0).astype('int32') 

        DataStore.df_cleaned.loc[DataStore.df_cleaned['frecuencia_compra'] == 0, 'frecuencia_compra'] = DataStore.df_cleaned["frecuencia_compra"].median()
        DataStore.df_cleaned.loc[DataStore.df_cleaned['dias_desde_ultima_compra'] == 0, 'dias_desde_ultima_compra'] = DataStore.df_cleaned["dias_desde_ultima_compra"].median()
        DataStore.df_cleaned.loc[DataStore.df_cleaned['antiguedad_cliente_meses'] == 0, 'antiguedad_cliente_meses'] = DataStore.df_cleaned["antiguedad_cliente_meses"].median()
        DataStore.df_cleaned.loc[DataStore.df_cleaned['numero_productos_distintos'] == 0, 'numero_productos_distintos'] = DataStore.df_cleaned["numero_productos_distintos"].median()

        DataStore.df_cleaned.loc[DataStore.df_cleaned['monto_total_gastado'] == 0, 'monto_total_gastado'] = DataStore.df_cleaned["monto_total_gastado"].mean()
        DataStore.df_cleaned.loc[DataStore.df_cleaned['monto_promedio_compra'] == 0, 'monto_promedio_compra'] = DataStore.df_cleaned["monto_promedio_compra"].mean()


        DataStore.df_cleaned["canal_principal"] = (DataStore.df_cleaned["canal_principal"].astype("string").fillna("Desconocido"))
        DataStore.df_cleaned["producto_categoria"] = (DataStore.df_cleaned["producto_categoria"].astype("string").fillna("Desconocido"))



 
        return jsonify({
            "success": True,
            "message": "Limpieza completada exitosamente",
            "statistics": {
                "initial_rows":len(DataStore.df_raw),
                "final_rows": len(DataStore.df_cleaned),
            },
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error durante la limpieza",
            "detail": str(e)
        }), 500


@clean_bp.get("/cleaned-data")
def get_cleaned_data():
    """Obtener vista previa de datos limpios"""
    if DataStore.df_cleaned is None:
        return jsonify({"error": "No se han limpiado datos aún"}), 400

    return jsonify({
        "rows": len(DataStore.df_cleaned),
        "columns": list(DataStore.df_cleaned.columns),
        "head": DataStore.df_cleaned.head(10).to_dict(orient="records"),
        "statistics": {
            "numeric_stats": DataStore.df_cleaned.describe().to_dict(),
            "null_counts": DataStore.df_cleaned.isnull().sum().to_dict(),
        }
    }), 200
