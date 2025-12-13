from flask import Blueprint, jsonify, request
import pandas as pd
from models import DataStore
from typing import Optional  


clean_bp = Blueprint("clean", __name__)


@clean_bp.get("/clean")
def cleanDataFrame():
    if DataStore.df_raw is None:
        return jsonify({"error": "No se ha cargado ningun archivo .csv"}), 400
    ##begin cleaning process

    #Delete extra columns
    DataStore.df_cleaned = DataStore.df_raw.drop(columns=["carnet", "first_name", "last_name", "gender"])

    #Delete duplicates
    DataStore.df_cleaned = DataStore.df_cleaned.drop_duplicates()
    
    #Types
    DataStore.df_cleaned["tareas_entregadas"] = pd.to_numeric(DataStore.df_cleaned["tareas_entregadas"], errors='coerce').fillna(0).astype('int32') #
    DataStore.df_cleaned["cursos_reprobados"] = pd.to_numeric(DataStore.df_cleaned["cursos_reprobados"], errors='coerce').fillna(0).astype('int32') #
    DataStore.df_cleaned["reportes_disciplinarios"] = pd.to_numeric(DataStore.df_cleaned["reportes_disciplinarios"], errors='coerce').fillna(0).astype('int32') #
    # pending: 10.4? 

    DataStore.df_cleaned["participacion_clase"] = pd.to_numeric(DataStore.df_cleaned["participacion_clase"], errors='coerce').fillna(0).astype('float32') #
    DataStore.df_cleaned["asistencia_clases"] = pd.to_numeric(DataStore.df_cleaned["asistencia_clases"], errors='coerce').fillna(0).astype('float32') #
    DataStore.df_cleaned["promedio_evaluaciones"] = pd.to_numeric(DataStore.df_cleaned["promedio_evaluaciones"], errors='coerce').fillna(0).astype('float32') #
    DataStore.df_cleaned["horas_estudio"] = pd.to_numeric(DataStore.df_cleaned["horas_estudio"], errors='coerce').fillna(0).astype('float32') #
    DataStore.df_cleaned["promedio_actual"] = pd.to_numeric(DataStore.df_cleaned["promedio_actual"], errors='coerce').fillna(0).astype('float32') #

    DataStore.df_cleaned["actividades_extracurriculares"]=DataStore.df_cleaned["actividades_extracurriculares"].str.strip().replace('"', '')
    DataStore.df_cleaned["actividades_extracurriculares"]=DataStore.df_cleaned["actividades_extracurriculares"].apply(eval)

    DataStore.df_cleaned["riesgo"]= DataStore.df_cleaned["riesgo"].str.strip().replace('riesgo','1', regex=False)
    DataStore.df_cleaned["riesgo"]= DataStore.df_cleaned["riesgo"].str.strip().replace('no riesgo', '0', regex=False)
    
    DataStore.df_cleaned["riesgo"] = pd.to_numeric(DataStore.df_cleaned["riesgo"]).astype('int32') #
    # print(DataStore.df_cleaned.describe())
    
    DataStore.df_cleaned.loc[DataStore.df_cleaned['tareas_entregadas'] == 0, 'tareas_entregadas'] = DataStore.df_cleaned["tareas_entregadas"].median()
    DataStore.df_cleaned.loc[DataStore.df_cleaned['participacion_clase'] == 0, 'participacion_clase'] = DataStore.df_cleaned["participacion_clase"].median()
    DataStore.df_cleaned.loc[DataStore.df_cleaned['asistencia_clases'] == 0, 'asistencia_clases'] = DataStore.df_cleaned["asistencia_clases"].median()
    DataStore.df_cleaned.loc[DataStore.df_cleaned['horas_estudio'] == 0, 'horas_estudio'] = DataStore.df_cleaned["horas_estudio"].median()
    DataStore.df_cleaned.loc[DataStore.df_cleaned['promedio_evaluaciones'] == 0, 'promedio_evaluaciones'] = DataStore.df_cleaned["promedio_evaluaciones"].mean()
    DataStore.df_cleaned.loc[DataStore.df_cleaned['promedio_actual'] == 0, 'promedio_actual'] = DataStore.df_cleaned["promedio_actual"].mean()


    # for i, l in enumerate(DataStore.df_cleaned["actividades_extracurriculares"]):
    #     status = "None" if l is None else ("Empty" if not l else l[0])
    #     print(f"list {i} is {status}")

    return jsonify({
        "message": "Se han limpiado los datos correctamente",
    }), 200

