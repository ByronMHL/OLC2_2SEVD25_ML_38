from typing import List, Dict, Any, Optional
import pandas as pd

# Léxico simple en español basado en lemas frecuentes.
# Nota: mantener palabras en minúsculas y en forma lematizada cuando sea posible.
POSITIVE_WORDS = {
	"bueno", "excelente", "fantástico", "genial", "positivo", "agradable",
	"rápido", "eficiente", "fácil", "amable", "satisfecho", "recomendado",
	"recomendar", "encantar", "mejor", "calidad", "perfecto", "útil",
	"contento", "feliz", "maravilloso", "impresionante"
}

NEGATIVE_WORDS = {
	"malo", "terrible", "horrible", "defectuoso", "lento", "difícil",
	"caro", "decepcionante", "decepcionado", "pésimo", "peor", "problema",
	"error", "fallo", "dañado", "insatisfecho", "negativo", "tarde",
	"incómodo", "frustrante", "inútil"
}


def _score_tokens(tokens: List[str]) -> float:
	"""Calcula un puntaje de sentimiento normalizado en [-1, 1]."""
	if not tokens:
		return 0.0
	pos = sum(1 for t in tokens if t in POSITIVE_WORDS)
	neg = sum(1 for t in tokens if t in NEGATIVE_WORDS)
	# Normalizar por longitud para evitar sesgo por reseñas largas
	score = (pos - neg) / max(1, len(tokens))
	# Escalar para hacer más visible el rango sin superar [-1,1]
	return max(-1.0, min(1.0, score * 3))


def _label_from_score(score: float) -> str:
	"""Devuelve etiqueta a partir del puntaje: positivo/neutral/negativo."""
	if score >= 0.2:
		return "positivo"
	if score <= -0.2:
		return "negativo"
	return "neutral"


# Cache del analizador de pysentimiento (si está disponible)
_ANALYZER_ES = None


def _ensure_pysentimiento():
	"""Intenta crear el analizador de pysentimiento para español."""
	global _ANALYZER_ES
	if _ANALYZER_ES is not None:
		return _ANALYZER_ES
	try:
		from pysentimiento import create_analyzer
		_ANALYZER_ES = create_analyzer(task="sentiment", lang="es")
		return _ANALYZER_ES
	except Exception:
		return None


def analyze_sentiments(
	df_text: pd.DataFrame,
	tokens_col: str = "lemmas",
	text_col: str = "texto_limpio"
) -> pd.DataFrame:
	"""
	Calcula sentimiento por reseña usando el texto limpio.

	- Prefiere `tokens_col` (lista de lemas) si existe; de lo contrario tokeniza por espacios en `text_col`.
	- Agrega columnas `sentiment_score` y `sentiment_label` al DataFrame copiado.
	"""
	if tokens_col not in df_text.columns and text_col not in df_text.columns:
		raise ValueError(f"Se requieren columnas '{tokens_col}' o '{text_col}' en df_text")

	df = df_text.copy()

	def _extract_tokens(row) -> List[str]:
		if tokens_col in df_text.columns and isinstance(row.get(tokens_col), list):
			return [str(t).lower() for t in row.get(tokens_col) if isinstance(t, str) and t]
		# Fallback: tokenizar por espacios desde texto_limpio
		text = str(row.get(text_col, "")).strip().lower()
		return [t for t in text.split() if t]
    
	analyzer = _ensure_pysentimiento()
	tokens_list: List[List[str]] = df.apply(_extract_tokens, axis=1)

	scores: List[float] = []
	labels: List[str] = []

	if analyzer is not None:
		# Usar pysentimiento con texto unido por espacios
		label_map = {"POS": "positivo", "NEG": "negativo", "NEU": "neutral"}
		for toks in tokens_list:
			text = " ".join(toks)
			try:
				res = analyzer.predict(text)
				probas = getattr(res, "probas", {})
				score = float(probas.get("POS", 0.0)) - float(probas.get("NEG", 0.0))
				label_raw = getattr(res, "output", None)
				label = label_map.get(str(label_raw), _label_from_score(score))
			except Exception:
				# Fallback por error puntual del modelo
				score = _score_tokens(toks)
				label = _label_from_score(score)
			scores.append(score)
			labels.append(label)
	else:
		# Fallback léxico si no está disponible pysentimiento
		scores = [_score_tokens(toks) for toks in tokens_list]
		labels = [_label_from_score(s) for s in scores]

	df["sentiment_score"] = scores
	df["sentiment_label"] = labels
	return df


def summarize_sentiments(df_with_sentiment: pd.DataFrame) -> Dict[str, Any]:
	"""Resumen agregado de sentimientos: conteos y promedio de puntajes."""
	if "sentiment_label" not in df_with_sentiment.columns or "sentiment_score" not in df_with_sentiment.columns:
		raise ValueError("El DataFrame debe contener 'sentiment_label' y 'sentiment_score'")

	total = int(len(df_with_sentiment))
	counts = df_with_sentiment["sentiment_label"].value_counts().to_dict()
	avg = float(df_with_sentiment["sentiment_score"].mean()) if total else 0.0

	return {
		"total": total,
		"counts": counts,
		"avg_score": avg,
	}

