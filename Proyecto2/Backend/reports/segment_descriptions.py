from typing import Dict, Any, List


def _describe_numeric_profile(profile: Dict[str, Any], z_high: float, z_low: float) -> List[str]:
    z = profile.get("zscore", {})
    lines = []
    highs = [k for k, v in z.items() if v >= z_high]
    lows = [k for k, v in z.items() if v <= z_low]

    if highs:
        lines.append("Destaca en: " + ", ".join(highs))
    if lows:
        lines.append("Bajo en: " + ", ".join(lows))
    if not lines:
        lines.append("Perfil balanceado sin desviaciones fuertes")
    return lines


def _describe_text_terms(cluster_terms: List[Dict[str, Any]]) -> str:
    terms = [t["term"] for t in cluster_terms[:6]]
    if terms:
        return "Temas frecuentes: " + ", ".join(terms)
    return "Sin términos destacados"


def build_segment_descriptions(numeric_profiles: Dict[str, Any], text_patterns: Dict[str, Any], z_high: float = 0.7, z_low: float = -0.7) -> Dict[str, Any]:
    """Genera descripciones interpretables por cluster combinando perfiles numéricos y patrones textuales.

    Parametriza umbrales de z-score con `z_high` y `z_low`.
    """
    profiles = numeric_profiles.get("profiles", {})
    text_clusters = text_patterns.get("clusters", {})

    descriptions: Dict[str, Any] = {"clusters": {}}

    for cl_key, prof in profiles.items():
        num_desc_lines = _describe_numeric_profile(prof, z_high=z_high, z_low=z_low)
        text_part = _describe_text_terms(text_clusters.get(cl_key, {}).get("top_terms", []))
        size = prof.get("size", 0)

        full_text = (
            f"Segmento {cl_key} (n={size}). "
            + "; ".join(num_desc_lines)
            + ". "
            + text_part
        )
        descriptions["clusters"][cl_key] = {
            "text": full_text,
            "size": size,
            "numeric_summary": num_desc_lines,
            "text_terms": text_clusters.get(cl_key, {}).get("top_terms", []),
        }

    return descriptions
