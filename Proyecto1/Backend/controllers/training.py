from flask import Blueprint, jsonify, request
import pandas as pd
from models import DataStore
from typing import Optional 
 
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split


from sklearn.linear_model import LogisticRegression #Modelo
from sklearn.ensemble import RandomForestClassifier #Modelo

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score


training_bp = Blueprint("training", __name__)
"""
    Begin: Preprocess
"""
@training_bp.get("/training")
def preprocess_and_split():
    numeric =["asistencia_clases",
            "tareas_entregadas",
            "participacion_clase",
            "horas_estudio",
            "promedio_evaluaciones",
            "cursos_reprobados",
            "reportes_disciplinarios",
            "promedio_actual"]
    
    # binc=["actividades_extracurriculares"] #Sin normalizar
        
    # Validar que exista df_cleaned del proceso de limpieza
    if getattr(DataStore, 'df_cleaned', None) is None:
        return jsonify({"error": "Primero ejecute la limpieza de datos (/clean)"}), 400


    """ Convertir actividades_extracurriculares en columnas binarias: (NORMALIZANDO)"""
    mlb = MultiLabelBinarizer() # lista a columnas
    # Temp dataframe
    actividades_encoded = pd.DataFrame(
        mlb.fit_transform(DataStore.df_cleaned['actividades_extracurriculares']),
        columns=mlb.classes_,
        index=DataStore.df_cleaned.index
    )

    # Sin normalizar
    # df_model = DataStore.df_cleaned.copy() 
  
    #normalizando      
    df_model = pd.concat([DataStore.df_cleaned, actividades_encoded], axis=1)
    df_model = df_model.drop(columns=['actividades_extracurriculares'])
    
    #Separar X e y
    if "riesgo" not in df_model.columns:
        return jsonify({"error": "La columna 'riesgo' es obligatoria para el entrenamiento"}), 400

    X = df_model.drop(columns=["riesgo"])
    y = df_model["riesgo"]



    preproc = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric),
        ('bin', 'passthrough', actividades_encoded.columns)
        # ('bin', 'passthrough', binc)
    ],
     remainder='drop'
)
    
    if X.isnull().any().any():
        return jsonify({"error": "Existen valores nulos en X después del preprocesamiento"}), 400

    if y.isnull().any():
        return jsonify({"error": "Existen valores nulos en y después del preprocesamiento"}), 400


    #MODELO 1

    pipeline_completo = Pipeline(steps=[
    ('preprocessor', preproc),
    ('classifier', RandomForestClassifier(
       n_estimators=1000,
       random_state=42,
    )
     )
    ])
    
    #MODELO 2 
    # pipeline_completo = Pipeline(steps=[
    # ('preprocessor', preproc),
    # ('classifier', LogisticRegression(
    #     max_iter=2000,
    #     class_weight='balanced',
    #     random_state=42
    # ))
    # ])
    
    
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42,stratify=y)


    # entrenar

    pipeline_completo.fit(X_train, y_train)


    #predict 
    y_pred = pipeline_completo.predict(X_test)
    y_proba = pipeline_completo.predict_proba(X_test)[:, 1] #Prob

    #Print for testing
    
    resultados = X_test.copy()
    resultados["riesgo_real"] = y_test.values
    resultados["prob_riesgo"] = y_proba
    resultados["riesgo_predicho"] = y_pred
    print("-"*100)

    print(resultados.head(20))


    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print("\nReporte completo:")
    print(classification_report(y_test, y_pred))
    
    # Guardar en DataStore para uso posterior
    DataStore.X = X
    DataStore.y = y

    metadata = {
        "rows": int(df_model.shape[0]),
        "cols_X": list(X.columns),
        "target": "riesgo",
        "class_balance": y.value_counts().to_dict(),
    }
    return jsonify({
        "message": "Preprocesamiento completado y separación X/y realizada",
        "metadata": metadata,
    }), 200





# @training_bp.get("/training")


#     return jsonify({
#         "message": "Preprocesamiento completado y separación X/y realizada",
#         "metadata": metadata,
#     }), 200
