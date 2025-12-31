from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
import re
from models import DataStore
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

clean_bp = Blueprint("clean", __name__)


def _ensure_nltk_resources():
    """Asegura recursos NLTK necesarios (stopwords, punkt, wordnet)."""
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)


# Cache del modelo spaCy en español (si está disponible)
_SPACY_NLP_ES = None
_NLTK_TOKENIZER_AVAILABLE = None


def _ensure_spacy_model():
    """Intenta cargar el modelo spaCy español; lo descarga si falta."""
    global _SPACY_NLP_ES
    if _SPACY_NLP_ES is not None:
        return _SPACY_NLP_ES
    try:
        import spacy
        from spacy.cli import download as spacy_download
    except Exception:
        return None
    try:
        _SPACY_NLP_ES = spacy.load("es_core_news_sm")
        return _SPACY_NLP_ES
    except Exception:
        try:
            spacy_download("es_core_news_sm")
            _SPACY_NLP_ES = spacy.load("es_core_news_sm")
            return _SPACY_NLP_ES
        except Exception:
            return None


def _ensure_nltk_resources():
    """Asegura recursos NLTK necesarios (stopwords, punkt/punkt_tab, wordnet)."""
    global _NLTK_TOKENIZER_AVAILABLE
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)

    # Asegurar tokenizer: probar tanto 'punkt' como 'punkt_tab'
    tokenizer_ok = False
    try:
        nltk.data.find('tokenizers/punkt')
        tokenizer_ok = True
    except LookupError:
        try:
            nltk.data.find('tokenizers/punkt_tab')
            tokenizer_ok = True
        except LookupError:
            # Intentar descargar ambos recursos
            try:
                nltk.download('punkt_tab', quiet=True)
            except Exception:
                pass
            try:
                nltk.download('punkt', quiet=True)
            except Exception:
                pass
            # Verificar nuevamente
            try:
                nltk.data.find('tokenizers/punkt_tab')
                tokenizer_ok = True
            except LookupError:
                try:
                    nltk.data.find('tokenizers/punkt')
                    tokenizer_ok = True
                except LookupError:
                    tokenizer_ok = False

    _NLTK_TOKENIZER_AVAILABLE = tokenizer_ok

    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)


def _get_spanish_stopwords_safe() -> set:
    """Obtiene stopwords de NLTK; si falla, usa un conjunto básico."""
    try:
        return set(stopwords.words('spanish'))
    except Exception as e:
        logging.warning(f"Stopwords NLTK no disponibles, usando fallback. Detalle: {e}")
        return {
            "el","la","los","las","de","del","y","en","es","un","una","unos","unas","al","a","con","por","para","como","se","su","sus","lo","le","les","o","u","que","qué","quien","quién","cual","cuál","donde","dónde","cuando","cuándo","mi","mis","tu","tus","nuestro","nuestra","nuestros","nuestras","pero","si","sí","no","ya","más","menos","muy","también","solo","sólo","porque","sobre","entre","hasta","desde","sin","todo","toda","todos","todas","cada","otro","otra","otros","otras"
        }


def _tokenize_spanish_safe(text: str) -> list:
    """Tokeniza en español; si falla NLTK, usa separación por espacios."""
    global _NLTK_TOKENIZER_AVAILABLE
    if _NLTK_TOKENIZER_AVAILABLE:
        try:
            return word_tokenize(text, language='spanish')
        except Exception as e:
            logging.warning(f"Tokenización NLTK falló, usando regex. Detalle: {e}")
            _NLTK_TOKENIZER_AVAILABLE = False
    # Fallback regex (sin log repetitivo)
    return [t for t in re.split(r"\s+", text.strip()) if t]


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
    # Normalizar nulos y espacios; registrar métricas iniciales de vacíos
    df_text["texto_reseña"] = df_text["texto_reseña"].astype("string").fillna("").str.strip()
    initial_rows = len(df_text)
    empty_original_count = int((df_text["texto_reseña"] == "").sum())
    df_text["texto_lower"] = df_text["texto_reseña"].str.lower()
    df_text["texto_sin_signos"] = df_text["texto_lower"].apply(lambda s: re.sub(r"[^\w\s]", " ", s))
    # Asegurar recursos y obtener stopwords de NLTK (español)
    _ensure_nltk_resources()
    STOPWORDS_ES = _get_spanish_stopwords_safe()
    # Tokenización segura y eliminación de stopwords
    df_text["tokens"] = df_text["texto_sin_signos"].apply(
        lambda s: [t for t in _tokenize_spanish_safe(s) if t and t.isalpha() and t not in STOPWORDS_ES]
    )
    # Lematización con spaCy si está disponible; si no, usar tokens como fallback
    nlp = _ensure_spacy_model()
    if nlp is not None:
        df_text["lemmas"] = df_text["texto_sin_signos"].apply(
            lambda s: [
                tok.lemma_.lower()
                for tok in nlp(s)
                if tok.is_alpha and tok.lemma_ and tok.lemma_.strip() and tok.lemma_.lower() not in STOPWORDS_ES
            ]
        )
    else:
        df_text["lemmas"] = df_text["tokens"]
    df_text["texto_limpio"] = df_text["lemmas"].apply(lambda toks: " ".join(toks))

    # Filtrar filas sin texto válido: original vacío o sin tokens/lemmas
    no_valid_tokens_count = int((df_text["lemmas"].apply(len) == 0).sum())
    # Primero descartar originales vacíos
    df_text = df_text[df_text["texto_reseña"] != ""]
    # Luego descartar entradas sin tokens/lemmas
    df_text = df_text[df_text["lemmas"].apply(lambda toks: len(toks) > 0)]
    df_text = df_text.copy().reset_index(drop=True)

    return {
        "df": df_text,
        "stats": {
            "initial_rows": initial_rows,
            "rows": len(df_text),
            "empty_text_count": empty_original_count,
            "no_valid_tokens_count": no_valid_tokens_count,
            "dropped_total": int(initial_rows - len(df_text)),
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
        # Preferir lemas si existen, de lo contrario tokens
        col = "lemmas" if "lemmas" in DataStore.df_text_cleaned.columns else "tokens"
        tokens_series = DataStore.df_text_cleaned[col]
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
