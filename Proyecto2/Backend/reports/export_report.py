import os
import json
from datetime import datetime
from typing import Dict, Any

from .segment_profiles import compute_numeric_profiles
from .segment_patterns import compute_text_patterns
from .segment_descriptions import build_segment_descriptions


def export_all_reports(cluster_col: str = None, top_n: int = 12, z_high: float = 0.7, z_low: float = -0.7) -> Dict[str, Any]:
    """Genera exportación completa (JSON + imágenes + tablas) organizada en carpeta por timestamp.

    Parametriza `top_n` para términos textuales y umbrales de z-score `z_high`/`z_low`.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_root = os.path.join(os.path.dirname(__file__), "exports", ts)
    os.makedirs(base_root, exist_ok=True)

    # Ejecutar cálculos
    numeric = compute_numeric_profiles(cluster_col=cluster_col, base_dir=base_root, use_subdir=False)
    text = compute_text_patterns(top_n=top_n, base_dir=base_root, use_subdir=False)
    descriptions = build_segment_descriptions(numeric, text, z_high=z_high, z_low=z_low)

    # Guardar resumen
    summary = {
        "timestamp": ts,
        "numeric_profiles": numeric,
        "text_patterns": text,
        "descriptions": descriptions,
    }
    summary_path = os.path.join(base_root, "report_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return {
        "export_root": base_root,
        "summary_path": summary_path,
        "sections": {
            "numeric_profiles": numeric,
            "text_patterns": text,
            "descriptions": descriptions,
        },
    }


# prune_exports eliminado según solicitud; export_all_reports permanece
