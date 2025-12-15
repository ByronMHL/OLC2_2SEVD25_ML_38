from flask import Blueprint, jsonify, request
import pandas as pd
from models import DataStore

from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os
import joblib

predict_bp = Blueprint("predict", __name__)


def _build_preprocessor_and_dataset():
	numeric = [
		"asistencia_clases",
		"tareas_entregadas",
		"participacion_clase",
		"horas_estudio",
		"promedio_evaluaciones",
		"cursos_reprobados",
		"reportes_disciplinarios",
		"promedio_actual",
	]

	if getattr(DataStore, "df_cleaned", None) is None:
		return None, None, None, None, {"error": "Primero ejecute la limpieza de datos (/clean)"}

	mlb = MultiLabelBinarizer()
	actividades_encoded = pd.DataFrame(
		mlb.fit_transform(DataStore.df_cleaned["actividades_extracurriculares"]),
		columns=mlb.classes_,
		index=DataStore.df_cleaned.index,
	)

	df_model = pd.concat([DataStore.df_cleaned, actividades_encoded], axis=1)
	df_model = df_model.drop(columns=["actividades_extracurriculares"])

	if "riesgo" not in df_model.columns:
		return None, None, None, None, {"error": "La columna 'riesgo' es obligatoria para el entrenamiento"}

	X = df_model.drop(columns=["riesgo"])
	y = df_model["riesgo"]

	preproc = ColumnTransformer(
		transformers=[
			("num", StandardScaler(), numeric),
			("bin", "passthrough", actividades_encoded.columns),
		],
		remainder="drop",
	)

	if X.isnull().any().any():
		return None, None, None, None, {"error": "Existen valores nulos en X después del preprocesamiento"}
	if y.isnull().any():
		return None, None, None, None, {"error": "Existen valores nulos en y después del preprocesamiento"}

	return X, y, preproc, mlb, None


def _build_pipeline(preproc):
	clf = RandomForestClassifier(n_estimators=1000, random_state=42)
	return Pipeline(steps=[("preprocessor", preproc), ("classifier", clf)])


@predict_bp.post("/predict")
def predict_one():
	payload = request.get_json(silent=True) or {}

	# Validar campos requeridos
	required_fields = [
		"promedio_actual",
		"asistencia_clases",
		"tareas_entregadas",
		"participacion_clase",
		"horas_estudio",
		"promedio_evaluaciones",
		"cursos_reprobados",
		"actividades_extracurriculares",
		"reportes_disciplinarios",
	]
	missing = [f for f in required_fields if f not in payload]
	if missing:
		return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

	# Intentar cargar un pipeline persistido (priorizar hiperparámetros si existe)
	models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
	pipe_hyper = os.path.join(models_dir, 'pipeline_hyper.pkl')
	pipe_training = os.path.join(models_dir, 'pipeline_training.pkl')

	pipeline = None
	mlb = None

	if os.path.exists(pipe_hyper):
		try:
			pipeline = joblib.load(pipe_hyper)
		except Exception as e:
			print(f"Error cargando pipeline_hyper.pkl: {e}")
	if pipeline is None and os.path.exists(pipe_training):
		try:
			pipeline = joblib.load(pipe_training)
		except Exception as e:
			print(f"Error cargando pipeline_training.pkl: {e}")

	# Si no existe un pipeline persistido, devolver error solicitando entrenamiento previo
	if pipeline is None:
		return jsonify({
			"error": "No hay un modelo entrenado. Ejecute primero /training o /training/randomsearch para generar el modelo (.pkl)."
		}), 400

	# Obtener columnas esperadas desde el preprocesador del pipeline guardado
	preproc = pipeline.named_steps.get("preprocessor") if hasattr(pipeline, "named_steps") else None
	if preproc is None:
		return jsonify({"error": "El modelo guardado no contiene un preprocesador válido"}), 500

	transformers_list = getattr(preproc, "transformers_", None) or getattr(preproc, "transformers", None)
	if transformers_list is None:
		return jsonify({"error": "No fue posible inspeccionar las columnas del preprocesador"}), 500

	num_cols = None
	bin_cols_expected = None
	for name, transformer, cols in transformers_list:
		if name == "num":
			num_cols = list(cols)
		if name == "bin":
			bin_cols_expected = list(cols)

	if bin_cols_expected is None or num_cols is None:
		return jsonify({"error": "El preprocesador del modelo no expone columnas 'num' y 'bin'"}), 500

	# Construir fila de entrada con misma estructura binaria
	actividades = payload.get("actividades_extracurriculares")
	if not isinstance(actividades, list):
		return jsonify({"error": "actividades_extracurriculares debe ser una lista"}), 400

	bin_cols = {col: (1 if col in actividades else 0) for col in bin_cols_expected}

	# Cargar numéricos dinámicamente según el modelo guardado
	row = {}
	for col in num_cols:
		if col not in payload:
			return jsonify({"error": f"Falta el campo numérico requerido: {col}"}), 400
		try:
			row[col] = float(payload[col])
		except Exception:
			return jsonify({"error": f"El campo {col} debe ser numérico"}), 400
	row.update(bin_cols)

	df_input = pd.DataFrame([row])

	# Predecir
	y_pred = pipeline.predict(df_input)[0]
	y_proba = pipeline.predict_proba(df_input)[0, 1]

	return jsonify({
		"prediccion": int(y_pred),
		"prob_riesgo": float(y_proba),
		"input": row,
	}), 200
