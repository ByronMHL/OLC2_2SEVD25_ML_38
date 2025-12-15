# Predicción

Este documento explica en detalle el flujo de predicción implementado en [controllers/predict.py](controllers/predict.py) y su relación con el módulo de entrenamiento [controllers/training.py](controllers/training.py).

## Visión General

- Endpoint: POST /api/predict
- Backend: Flask Blueprint predict_bp
- Modelo: RandomForestClassifier con un Pipeline que incluye ColumnTransformer para preprocesamiento.
- Entrada: un solo registro (instancia) con los mismos campos usados en el dataset limpio (df_cleaned).
- Salida: prediccion (0/1), prob_riesgo (probabilidad de clase 1) y input (fila normalizada enviada al modelo).

## Estructura del Código

- Blueprint y dependencias: ver [controllers/predict.py](controllers/predict.py).
- Funciones internas clave:
  - _build_preprocessor_and_dataset()
    - Construye el dataset modelable a partir de DataStore.df_cleaned.
    - Convierte actividades_extracurriculares en columnas binarias usando MultiLabelBinarizer.
    - Define el ColumnTransformer con:
      - Transformación numérica: StandardScaler sobre columnas numéricas.
      - Transformación binaria: passthrough sobre columnas resultantes del binarizado de actividades.
    - Valida presencia de df_cleaned, columna objetivo riesgo y ausencia de nulos.
    - Retorna (X, y, preproc, mlb, err).
  - _build_pipeline(preproc)
    - Define un Pipeline con etapas preprocessor (el ColumnTransformer) y classifier (RandomForestClassifier con n_estimators=1000, random_state=42).

- Endpoint @predict_bp.post("/predict"):
  1. Lee el payload JSON y valida campos requeridos:
     - promedio_actual, asistencia_clases, tareas_entregadas, participacion_clase, horas_estudio, promedio_evaluaciones, cursos_reprobados, actividades_extracurriculares, reportes_disciplinarios.
  2. Llama a _build_preprocessor_and_dataset() para obtener X, y, el preprocesador y el mlb.
     - Si falta df_cleaned o hay problemas de nulos/objetivo, retorna error.
  3. Divide el dataset (train_test_split) y entrena un Pipeline fresco con los datos actuales:
     - pipeline = _build_pipeline(preproc)
     - pipeline.fit(X_train, y_train)
  4. Construye la fila de entrada:
     - Verifica que actividades_extracurriculares sea una lista.
     - Genera columnas binarias para actividades con los nombres de mlb.classes_.
     - Arma un DataFrame de una sola fila con las columnas numéricas y binarias.
  5. Predice:
     - y_pred = pipeline.predict(df_input)[0]
     - y_proba = pipeline.predict_proba(df_input)[0, 1]
  6. Respuesta:
     - { prediccion: int, prob_riesgo: float, input: row }

## ¿Usa el Entrenamiento de training.py?

- No requiere haber ejecutado el endpoint de entrenamiento GET /api/training previamente para poder predecir.
- Sí requiere que el proceso de limpieza haya sido ejecutado antes (GET /api/clean) para que DataStore.df_cleaned exista y se pueda construir el preprocesamiento.
- En el flujo actual, el endpoint de predicción entrena un Pipeline nuevo en tiempo de petición con el dataset presente en memoria (derivado de df_cleaned). Por ello:
  - No reutiliza un modelo “persistido” por training.py.
  - Se garantiza que el preprocesamiento y el espacio de características (incluyendo las columnas binarias de actividades) estén alineados con el dataset actual.

### Pros y Contras de Entrenar en el Endpoint

- Pros:
  - Consistencia inmediata con el dataset limpio y sus columnas.
  - Evita desalineaciones entre el preprocesamiento y el modelo.
- Contras:
  - Coste computacional por cada predicción (entrenar en cada request no escala para alta concurrencia).
  - No aprovecha modelos ajustados mediante RandomizedSearchCV (ver [controllers/hyperparameters.py](controllers/hyperparameters.py)).

## Conexión con el Frontend

- El frontend envía POST /api/predict con un payload que incluye los valores numéricos y la lista de actividades_extracurriculares.
- La página de Predicción construye la lista desde una entrada separada por comas, valida rangos (0–100 para porcentajes, no negativos para contadores) y muestra:
  - Etiqueta de riesgo (alto/bajo).
  - Barra de probabilidad con el porcentaje.
  - Iconografía visual dependiente del umbral.

## Requisitos y Validaciones

- Requiere que exista DataStore.df_cleaned (ejecutar /api/clean).
- Requiere columna riesgo en el dataset.
- Rechaza actividades_extracurriculares si no es lista.
- Verifica ausencia de nulos en X e y antes de entrenar.

## Extensiones Futuras

- Persistir y reutilizar el modelo entrenado por training.py o el mejor modelo de RandomizedSearchCV del módulo [controllers/hyperparameters.py](controllers/hyperparameters.py).
- Introducir caché del Pipeline entrenado para reducir latencia en predicciones repetidas.
- Validaciones adicionales de rangos en backend (además de las que ya hace el frontend).

## Archivos Relacionados

- Entrenamiento: [controllers/training.py](controllers/training.py)
- Ajuste de hiperparámetros (RandomizedSearchCV): [controllers/hyperparameters.py](controllers/hyperparameters.py)
- Limpieza de datos: [controllers/clean.py](controllers/clean.py)
