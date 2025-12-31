import os
import json
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Estilo consistente y legible para figuras
sns.set_theme(style="darkgrid", palette="deep")

from models import DataStore

EXPECTED_NUM_COLS = [
    "frecuencia_compra",
    "monto_total_gastado",
    "monto_promedio_compra",
    "dias_desde_ultima_compra",
    "antiguedad_cliente_meses",
    "numero_productos_distintos",
]


def _ensure_dirs(base_dir: str) -> Dict[str, str]:
    figures_dir = os.path.join(base_dir, "figures")
    tables_dir = os.path.join(base_dir, "tables")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)
    return {"figures": figures_dir, "tables": tables_dir}


def compute_numeric_profiles(cluster_col: str = None, base_dir: str = "exports", use_subdir: bool = True) -> Dict[str, Any]:
    """Calcula perfil estadístico por segmento y genera gráficos de apoyo.
    Retorna estructura lista para frontend con paths a figuras y tablas.
    """
    if getattr(DataStore, "df_numeric_cleaned", None) is None:
        raise ValueError("No hay datos numéricos limpios disponibles. Ejecute /clean primero.")

    df = DataStore.df_numeric_cleaned.copy()

    # Seleccionar columna de cluster
    if cluster_col is None:
        if "kmeans_cluster" in df.columns:
            cluster_col = "kmeans_cluster"
        elif "hierarchical_cluster" in df.columns:
            cluster_col = "hierarchical_cluster"
        else:
            raise ValueError("No se encuentran columnas de cluster (kmeans_cluster|hierarchical_cluster).")

    # Seleccionar columnas numéricas presentes
    num_cols = [c for c in EXPECTED_NUM_COLS if c in df.columns]
    if not num_cols:
        raise ValueError("No hay columnas numéricas válidas para el perfilado.")

    # Usar base_dir (permitiendo rutas absolutas o relativas)
    if not os.path.isabs(base_dir):
        base_dir = os.path.join(os.path.dirname(__file__), base_dir)
    # Crear subcarpeta única para evitar caché/sobrescritura si se solicita
    run_dir = base_dir
    if use_subdir:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(base_dir, run_id)
    dirs = _ensure_dirs(run_dir)

    # Tabla resumen por cluster
    grouped = df.groupby(cluster_col)[num_cols]
    stats_mean = grouped.mean()
    stats_median = grouped.median()
    stats_p25 = grouped.quantile(0.25)
    stats_p75 = grouped.quantile(0.75)
    sizes = grouped.size().rename("size")

    # Z-scores por cluster (comparado con media global)
    global_mean = df[num_cols].mean()
    global_std = df[num_cols].std().replace(0, np.nan)
    zscores = (stats_mean - global_mean) / global_std

    # Guardar tablas
    summary_table = pd.concat(
        [stats_mean.add_suffix("_mean"), stats_median.add_suffix("_median"), stats_p25.add_suffix("_p25"), stats_p75.add_suffix("_p75"), sizes],
        axis=1
    )
    summary_csv_path = os.path.join(dirs["tables"], "numeric_profiles_summary.csv")
    summary_table.to_csv(summary_csv_path, index=True)

    # Gráficos: barras de medias por feature
    figures_paths: List[str] = []
    for col in num_cols:
        plt.figure(figsize=(8, 4))
        sns.barplot(x=stats_mean.index.astype(str), y=stats_mean[col], color="#4C78A8")
        plt.title(f"Media por cluster - {col}")
        plt.xlabel("Cluster")
        plt.ylabel("Media")
        path = os.path.join(dirs["figures"], f"bar_mean_{col}.png")
        plt.tight_layout()
        plt.savefig(path, transparent=False)
        plt.close()
        figures_paths.append(path)

    # Gráficos: boxplots por feature
    for col in num_cols:
        plt.figure(figsize=(8, 4))
        sns.boxplot(data=df[[cluster_col, col]], x=cluster_col, y=col)
        plt.title(f"Boxplot por cluster - {col}")
        plt.xlabel("Cluster")
        plt.ylabel(col)
        path = os.path.join(dirs["figures"], f"box_{col}.png")
        plt.tight_layout()
        plt.savefig(path, transparent=False)
        plt.close()
        figures_paths.append(path)

    # Construir respuesta estructurada
    profiles: Dict[str, Any] = {}
    for cl in stats_mean.index:
        cl_key = str(cl)
        profiles[cl_key] = {
            "size": int(sizes.loc[cl]),
            "mean": {k: float(stats_mean.loc[cl, k]) for k in num_cols},
            "median": {k: float(stats_median.loc[cl, k]) for k in num_cols},
            "p25": {k: float(stats_p25.loc[cl, k]) for k in num_cols},
            "p75": {k: float(stats_p75.loc[cl, k]) for k in num_cols},
            "zscore": {k: float(zscores.loc[cl, k]) if not np.isnan(zscores.loc[cl, k]) else 0.0 for k in num_cols},
        }

    result = {
        "cluster_col": cluster_col,
        "num_features": num_cols,
        "profiles": profiles,
        "tables": {"summary_csv": summary_csv_path},
        "figures": figures_paths,
        "run_dir": run_dir,
    }

    # Guardar JSON
    json_path = os.path.join(dirs["tables"], "numeric_profiles.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    result["tables"]["summary_json"] = json_path
    return result
