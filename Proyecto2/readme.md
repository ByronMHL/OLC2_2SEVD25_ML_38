# Proyecto 2: Segmentación de Clientes y Agrupamiento de Reseñas

## Descripción General

Aplicación integrada que implementa técnicas de aprendizaje no supervisado para realizar la segmentación de clientes y agrupamiento de reseñas de productos, con el fin de descubrir patrones ocultos en los datos.

## Características Principales

### 1. Carga Masiva de Datos
- Validación de formato CSV
- Verificación de columnas requeridas
- Manejo de archivos hasta 50MB
- Vista previa de datos cargados

### 2. Limpieza y Preprocesamiento
- Eliminación automática de duplicados
- Conversión segura de tipos de datos
- Manejo inteligente de valores faltantes:
  - Mediana para variables numéricas
  - Moda para variables categóricas
- Validación de valores negativos
- Codificación de variables categóricas
- Cálculo de características derivadas

### 3. Configuración de Modelos
- Parámetros ajustables para K-means:
  - Número de clusters (n_clusters)
  - Método de inicialización
  - Número de inicializaciones
  - Máximo de iteraciones
  - Semilla aleatoria (reproducibilidad)
  
- Parámetros ajustables para Hierarchical Clustering:
  - Número de clusters
  - Método de enlace (ward, complete, average, single)

### 4. Dos Algoritmos de Clustering

#### K-means
- Algoritmo de particionamiento rápido y eficiente
- Ideal para datasets grandes
- Requiere especificar número de clusters
- Métricas: Inertia, Silhouette, Davies-Bouldin, Calinski-Harabasz

#### Hierarchical Clustering (Agglomerative)
- Método jerárquico sin necesidad de especificar k
- Producción de dendrogramas informativos
- Mejor para análisis exploratorio
- Métricas: Silhouette, Davies-Bouldin, Calinski-Harabasz

### 5. Evaluación de Modelos
- **Silhouette Score**: Similitud dentro de clusters vs. separación entre clusters
- **Davies-Bouldin Index**: Compacidad vs. separación (menor es mejor)
- **Calinski-Harabasz Index**: Razón entre varianza inter-cluster e intra-cluster
- **Inertia** (K-means): Suma de distancias cuadradas

### 6. Predicción y Análisis
- Asignación de nuevos clientes a clusters
- Estadísticas por cluster
- Distribución de clientes
- Comparación de resultados entre modelos

## Arquitectura

```
Proyecto2/
├── Backend/
│   ├── main.py                 # Aplicación Flask principal
│   ├── models.py              # Almacén de datos y modelos
│   ├── requirements.txt        # Dependencias
│   ├── readme.md              # Documentación detallada
│   ├── test_api.py            # Suite de pruebas
│   └── controllers/
│       ├── upload.py          # Carga de CSV
│       ├── clean.py           # Limpieza/preprocesamiento
│       ├── training.py        # Entrenamiento de modelos
│       ├── hyperparameters.py # Configuración
│       └── predict.py         # Predicción/análisis
├── data/
│   └── data_prueba_proyecto2.csv  # Datos de prueba
├── Frontend/                  # (Por desarrollar)
├── notebooks/                 # (Por desarrollar)
├── QUICKSTART.md             # Guía de inicio rápido
└── readme.md                 # Este archivo
```

## Variables del Dataset

### Campos de Clientes
- **cliente_id**: Identificador único del cliente
- **frecuencia_compra**: Número de compras realizadas en un periodo
- **monto_total_gastado**: Gasto acumulado del cliente
- **monto_promedio_compra**: Promedio gastado por compra
- **dias_desde_ultima_compra**: Tiempo transcurrido desde la última compra
- **antiguedad_cliente_meses**: Tiempo que lleva como cliente
- **canal_principal**: Canal más utilizado (web, móvil, tienda física, marketplace, call center)
- **numero_productos_distintos**: Cantidad de categorías/productos comprados

### Campos de Reseñas
- **reseña_id**: Identificador único de la reseña
- **texto_reseña**: Opinión escrita por el cliente
- **fecha_reseña**: Fecha en que se realizó la reseña
- **producto_categoria**: Categoría del producto (ropa, electronica, alimentos, etc.)
- **longitud_reseña**: Número de caracteres (calculado automáticamente)

## Endpoints Principales

### Carga
- `POST /api/upload` - Cargar CSV
- `GET /api/raw-data` - Ver datos cargados

### Limpieza
- `GET /api/clean` - Limpiar y preprocesar
- `GET /api/cleaned-data` - Ver datos limpios

### Configuración
- `GET /api/hyperparameters/all` - Ver todos los parámetros
- `POST /api/hyperparameters/kmeans` - Configurar K-means
- `POST /api/hyperparameters/hierarchical` - Configurar Hierarchical

### Entrenamiento
- `POST /api/train/kmeans` - Entrenar K-means
- `POST /api/train/hierarchical` - Entrenar Hierarchical
- `POST /api/train/auto-k` - Entrenar K-means con K automático
- `GET /api/models/status` - Ver estado de modelos

### Resultados
- `GET /api/results/kmeans` - Resultados de K-means
- `GET /api/results/hierarchical` - Resultados de Hierarchical
- `GET /api/results/comparison` - Comparar modelos

### Predicción
- `POST /api/predict/kmeans` - Predecir con K-means
- `POST /api/predict/hierarchical` - Info de Hierarchical Clustering

## Instalación y Uso

### Instalación
```bash
cd Backend
pip install -r requirements.txt
```

### Ejecución
```bash
python main.py
```

### Pruebas
```bash
python test_api.py
```

Ver `QUICKSTART.md` para ejemplos de uso.

## Flujo de Uso Típico

1. **Cargar CSV** → Validar estructura
2. **Limpiar datos** → Preprocesamiento automático
3. **Configurar parámetros** (opcional) → Ajustar modelos
4. **Entrenar modelos** → Ejecutar K-means y/o Hierarchical
5. **Analizar resultados** → Ver métricas y estadísticas
6. **Comparar** → Evaluar rendimiento de ambos modelos
7. **Predecir** → Asignar nuevos clientes a clusters

## Tecnologías Utilizadas

### Backend
- **Flask 3.0.0** - Framework web
- **pandas 2.2.3** - Manipulación de datos
- **scikit-learn 1.4.2** - Machine Learning
- **numpy 1.24.3** - Computación numérica
- **flask-cors 4.0.0** - CORS para frontend

### Algoritmos
- **K-means** - Clustering por particionamiento
- **Hierarchical Clustering** - Clustering jerárquico
- **StandardScaler** - Normalización de features
- **Silhouette, Davies-Bouldin, Calinski-Harabasz** - Métricas

## Datos de Prueba

El proyecto incluye `data_prueba_proyecto2.csv` con 132 registros de clientes para pruebas inmediatas.

Contenidos:
- 132 clientes únicos
- 8 canales de compra diferentes
- 7 categorías de productos
- Datos con algunos valores faltantes (realistas)

## Métricas de Evaluación

### Silhouette Score
- **Rango**: -1 a 1
- **Interpretación**: >0.5 = bueno, >0.7 = excelente
- **Mide**: Similitud intra-cluster vs. separación inter-cluster

### Davies-Bouldin Index
- **Rango**: 0 a ∞
- **Interpretación**: Menor es mejor
- **Mide**: Promedio de similaridad entre cada cluster y su más similar

### Calinski-Harabasz Index
- **Rango**: 0 a ∞
- **Interpretación**: Mayor es mejor
- **Mide**: Razón entre varianza inter-cluster e intra-cluster

### Inertia (solo K-means)
- **Rango**: 0 a ∞
- **Interpretación**: Menor es mejor
- **Mide**: Suma de distancias cuadradas al centroide más cercano

## Casos de Uso

1. **Segmentación de Clientes para Marketing**
   - Identificar grupos con comportamiento similar
   - Diseñar estrategias personalizadas por segmento

2. **Análisis de Reseñas**
   - Agrupar reseñas por sentimiento o categoría
   - Identificar temas recurrentes

3. **RFM Analysis (Recency, Frequency, Monetary)**
   - Usar clustering para identificar clientes valiosos
   - Definir estrategias de retención

4. **Detección de Anomalías**
   - Identificar clientes con comportamiento atípico
   - Validar integridad de datos

## Próximos Pasos

- [ ] Implementar Frontend (Vite + React)
- [ ] Agregar análisis de texto (NLP) para reseñas
- [ ] Implementar más algoritmos (DBSCAN, Gaussian Mixture Models)
- [ ] Exportar resultados a CSV/JSON
- [ ] Visualizaciones interactivas
- [ ] Base de datos persistente
- [ ] Autenticación de usuarios

## Notas Importantes

- Los datos se almacenan en memoria durante la sesión
- Se recomienda usar K automático para datasets pequeños
- Para reproducibilidad: usar `random_state=42`
- Normalización automática mediante StandardScaler
- Todos los valores faltantes se tratan automáticamente

## Soporte y Contacto

Para preguntas o reportar problemas, consultar la documentación en:
- `readme.md` - Documentación técnica completa
- `QUICKSTART.md` - Guía de inicio rápido
- `Backend/readme.md` - Documentación de API

---

**Versión**: 1.0  
**Última actualización**: Diciembre 2025  
**Estado**: Funcional y listo para usar
