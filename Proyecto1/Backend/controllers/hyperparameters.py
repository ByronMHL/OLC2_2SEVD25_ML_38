from flask import Blueprint, jsonify, request
import pandas as pd
from models import DataStore

from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import os
import joblib

hyper_bp = Blueprint("hyperparams", __name__)


def build_dataset_and_preprocessor():
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
		return None, None, None, {"error": "Primero ejecute la limpieza de datos (/clean)"}

	mlb = MultiLabelBinarizer()
	actividades_encoded = pd.DataFrame(
		mlb.fit_transform(DataStore.df_cleaned["actividades_extracurriculares"]),
		columns=mlb.classes_,
		index=DataStore.df_cleaned.index,
	)

	df_model = pd.concat([DataStore.df_cleaned, actividades_encoded], axis=1)
	df_model = df_model.drop(columns=["actividades_extracurriculares"])

	if "riesgo" not in df_model.columns:
		return None, None, None, {"error": "La columna 'riesgo' es obligatoria para el entrenamiento"}

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
		return None, None, None, {"error": "Existen valores nulos en X después del preprocesamiento"}
	if y.isnull().any():
		return None, None, None, {"error": "Existen valores nulos en y después del preprocesamiento"}

	return X, y, preproc, None


def build_pipeline(preproc, rf_params=None):
	clf = RandomForestClassifier(**(rf_params or {}))
	return Pipeline(steps=[("preprocessor", preproc), ("classifier", clf)])


def evaluate_pipeline(pipeline, X_test, y_test):
	y_pred = pipeline.predict(X_test)
	y_proba = pipeline.predict_proba(X_test)[:, 1]

	resultados = X_test.copy()
	resultados["riesgo_real"] = y_test.values
	resultados["prob_riesgo"] = y_proba
	resultados["riesgo_predicho"] = y_pred

	accuracy = accuracy_score(y_test, y_pred)
	precision = precision_score(y_test, y_pred)
	recall = recall_score(y_test, y_pred)
	f1 = f1_score(y_test, y_pred)

	metrics = {
		"accuracy": float(accuracy),
		"precision": float(precision),
		"recall": float(recall),
		"f1": float(f1),
	}

	sample = resultados.head(20)
	results = {
		"columns": list(sample.columns),
		"rows": sample.to_dict(orient="records"),
	}

	return metrics, results


# RandomizedSearchCV

@hyper_bp.post("/training/randomsearch")
def rf_random_search():
	payload = request.get_json(silent=True) or {}
	X, y, preproc, err = build_dataset_and_preprocessor()
	if err:
		return jsonify(err), 400

	X_train, X_test, y_train, y_test = train_test_split(
		X, y, test_size=0.2, random_state=42, stratify=y
	)

	pipeline = build_pipeline(preproc)

	# Límites sensatos y parámetros ajustables (sólo n_iter y cv desde el frontend)
	n_iter = max(1, min(int(payload.get("n_iter", 20)), 200))
	cv = max(2, min(int(payload.get("cv", 3)), 10))

	# Espacio estable por defecto
	param_dist = {
		"classifier__n_estimators": [100, 300, 500, 800, 1000],
		"classifier__max_depth": [10, 20, 30, 40, 50],
		"classifier__min_samples_split": [2, 5, 10],
		"classifier__min_samples_leaf": [1, 2],
		"classifier__bootstrap": [True],
		"classifier__max_features": ["sqrt", "log2"],
	}

	rand = RandomizedSearchCV(
		estimator=pipeline,
		param_distributions=param_dist,
		n_iter=n_iter,
		scoring="f1",
		cv=cv,
		random_state=42,
		n_jobs=-1,
		verbose=0,
	)
	rand.fit(X_train, y_train)

	best_pipeline = rand.best_estimator_
	metrics, results = evaluate_pipeline(best_pipeline, X_test, y_test)

	# Persistir el mejor pipeline para reutilizar en predicción
	models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
	os.makedirs(models_dir, exist_ok=True)
	model_path = os.path.join(models_dir, 'pipeline_hyper.pkl')
	try:
		joblib.dump(best_pipeline, model_path)
	except Exception as e:
		print(f"No se pudo guardar el modelo de hyperparameters: {e}")

	response = {
		"message": "RandomizedSearchCV completado",
		"best_params": rand.best_params_,
		"best_score_cv": float(rand.best_score_),
		"metrics": metrics,
		"results": results,
		"search_config": {"n_iter": n_iter, "cv": cv},
		"model_path": model_path,
	}
	return jsonify(response), 200