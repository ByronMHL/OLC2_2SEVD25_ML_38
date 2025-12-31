# Backend Proyecto 2 - API de Clustering

## Descripción General
API para cargar archivos CSV, limpiar datos, entrenar modelos de clustering (K-Means y Hierarchical Clustering) y realizar análisis textual mediante TF-IDF y K-Means. Utiliza Flask como framework web y scikit-learn para el procesamiento y modelado.

---

## Endpoints Principales
- **GET /api/health**: Verifica el estado del servicio.
- **POST /api/upload**: Recibe un archivo CSV y valida columnas requeridas.
- **GET /api/clean**: Limpia y preprocesa los datos.
- **GET /api/clean-text**: Limpieza textual para clustering basado en texto.
- **POST /api/train/kmeans**: Entrena modelo K-means.
- **POST /api/train/hierarchical**: Entrena modelo Hierarchical Clustering.
- **GET /api/results/kmeans**: Obtiene resultados de K-means.
- **GET /api/results/hierarchical**: Obtiene resultados de Hierarchical.
- **GET /api/training/text/kmeans**: Entrena K-Means sobre datos textuales.

Columnas requeridas en el CSV:
`cliente_id`, `frecuencia_compra`, `monto_total_gastado`, `monto_promedio_compra`, `dias_desde_ultima_compra`, `antiguedad_cliente_meses`, `canal_principal`, `numero_productos_distintos`, `texto_reseña`.

---

## Algoritmos Utilizados

### K-Means Clustering
El algoritmo K-Means se utiliza para agrupar datos numéricos en clústeres. Se implementó con las siguientes características:
- **Librería**: scikit-learn
- **Hiperparámetros**:
  - `n_clusters`: Número de clústeres (por defecto 6).
  - `init`: Método de inicialización (`k-means++` o `random`).
  - `n_init`: Número de inicializaciones (por defecto 10).
  - `max_iter`: Iteraciones máximas (por defecto 500).
  - `random_state`: Semilla para reproducibilidad.

### Hierarchical Clustering
Se implementó el algoritmo de clustering jerárquico para agrupar datos numéricos. Este utiliza métricas de distancia para construir una jerarquía de clústeres.

### Clustering Textual (TF-IDF + K-Means)
Para datos textuales, se utilizó una combinación de TF-IDF y K-Means:
- **TF-IDF**: Vectorización de texto para convertirlo en una representación numérica.
- **K-Means**: Agrupación de los vectores TF-IDF en clústeres.
- **Métricas**:
  - `silhouette_score` (cosine).
  - `davies_bouldin_score`.
  - `calinski_harabasz_score`.

---

## Proceso de Limpieza de Datos

### Limpieza Numérica
- Eliminación de columnas irrelevantes.
- Imputación de valores faltantes con la mediana o media.
- Conversión de columnas categóricas a valores conocidos.

### Limpieza Textual
- Conversión a minúsculas.
- Eliminación de signos de puntuación.

---

## Hiperparámetros (Entrenamiento)

### K-Means
- `n_clusters`: Número de clústeres (mínimo 2).
- `init`: Método de inicialización (`k-means++` o `random`).
- `n_init`: Número de inicializaciones (mínimo 1).
- `max_iter`: Iteraciones máximas (mínimo 1).
- `random_state`: Semilla para reproducibilidad.

### TF-IDF
- `max_features`: Número máximo de características (por defecto 2000).
- `min_df`: Frecuencia mínima de documentos (por defecto 3).
- `max_df`: Frecuencia máxima de documentos (por defecto 0.7).
- `ngram_range`: Rango de n-gramas (por defecto (1, 2)).
- `sublinear_tf`: Escalado sublineal (por defecto True).

---

## Justificación 

### Enfoque General
El enfoque adoptado para este proyecto se centra en la implementación de algoritmos de clustering debido a su capacidad para identificar patrones y agrupar datos sin necesidad de etiquetas predefinidas. 
### Justificación de K-Means

- **Simplicidad y Eficiencia**: Se utilizo debido a su simplicidad y eficiencia computacional, especialmente en conjuntos de datos grandes.
- **Flexibilidad**: Permite ajustar el número de clústeres (`n_clusters`) para adaptarse a diferentes necesidades analíticas.
- **Interpretabilidad**: Los resultados son fáciles de interpretar, ya que cada punto se asigna al clúster más cercano.

### Justificación de Hierarchical Clustering
- **Visualización**: Facilidad para la visualización de las relaciones jerárquicas entre los datos.
- **Sin necesidad de predefinir clústeres**: A diferencia de K-Means, no requiere especificar el número de clústeres de antemano.
- **Complementariedad**: Es útil para validar los resultados obtenidos con K-Means y explorar diferentes niveles de granularidad en los datos.

### Justificación del Clustering Textual (TF-IDF + K-Means)
- **Representación Numérica del Texto**: TF-IDF convierte texto en vectores numéricos, lo que permite aplicar algoritmos de clustering.
- **Identificación de Patrones en Texto**: La combinación de TF-IDF y K-Means facilito la agrupación de documentos o frases similares, por lo que en el análisis de sentimientos, categorización de temas, se obtuvo un mejor resultado .
- **Métricas de Evaluación**: Se utilizan métricas como `silhouette_score`, `davies_bouldin_score` y `calinski_harabasz_score` para evaluar la calidad de los clústeres generados.

### Consideraciones Finales
El enfoque seleccionado equilibra simplicidad, eficiencia y flexibilidad, permitiendo abordar tanto datos numéricos como textuales. Además, la capacidad de ajustar hiperparámetros clave asegura que los modelos puedan optimizarse para diferentes conjuntos de datos y objetivos analíticos.

---

## Conclusiones

1. **Eficiencia de los Algoritmos**: Los algoritmos de clustering implementados demostraron ser efectivos para agrupar datos tanto numéricos como textuales, pero se contempla el archivo de entrada y su ruido.
2. **Importancia de la Limpieza de Datos**: La calidad de los datos de entrada es crucial para obtener resultados precisos en los modelos de clustering.
3. **Flexibilidad**: La API permite ajustar hiperparámetros clave, lo que facilita la experimentación y optimización de los modelos.
4. **Desafíos para el entranmiento**: La limpieza textual y la vectorización TF-IDF pueden ser costosas en términos de tiempo para grandes volúmenes de datos.

---

## Instalación y Ejecución

1. Crear y activar un entorno virtual (opcional).
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar el servidor:
   ```bash
   python main.py
   ```

---

## Pruebas

Probar en Postman:
- **Método**: POST
- **URL**: http://localhost:5000/api/upload
- **Body**: form-data, key: `file` (tipo File), valor: seleccionar CSV.

Respuesta exitosa (200):
```json
{
  "message": "Archivo CSV recibido y validado",
  "saved_to": "ruta",
  "rows": 132,
  "columns": ["..."],
  "extra_columns": ["..."]
}
```

Errores comunes:
- **400**: Nombre de archivo vacío o faltan columnas requeridas.
- **400**: Formato inválido (no CSV) o CSV no legible.
