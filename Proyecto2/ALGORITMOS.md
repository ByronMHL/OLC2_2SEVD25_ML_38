# Algoritmos de Clustering - Documentación Técnica

## Introducción

Este documento explica en detalle los dos algoritmos de clustering implementados en el backend: **K-means** y **Hierarchical Clustering**.

## 1. K-means

### ¿Qué es K-means?

K-means es un algoritmo de **clustering por particionamiento** que divide los datos en K grupos (clusters) donde cada punto pertenece al cluster cuyo centroide es más cercano.

### Algoritmo

1. **Inicialización**: Seleccionar K puntos iniciales como centroides
   - `random`: Elegir K puntos aleatorios
   - `k-means++`: Seleccionar puntos que estén bien distribuidos (recomendado)

2. **Asignación**: Asignar cada punto al cluster cuyo centroide es más cercano

3. **Actualización**: Recalcular los centroides como la media de todos los puntos en cada cluster

4. **Repetir**: Continuar hasta convergencia (sin cambios o máximo de iteraciones)

### Implementación

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Normalizar datos
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Entrenar K-means
kmeans = KMeans(
    n_clusters=3,           # Número de clusters
    init='k-means++',       # Método de inicialización
    n_init=10,              # Número de ejecuciones
    max_iter=300,           # Máximo de iteraciones
    random_state=42         # Reproducibilidad
)

labels = kmeans.fit_predict(features_scaled)
```

### Parámetros Clave

| Parámetro | Rango | Defecto | Descripción |
|-----------|-------|---------|-------------|
| n_clusters | 2+ | 3 | Número de clusters |
| init | k-means++, random | k-means++ | Método de inicialización |
| n_init | 1+ | 10 | Número de ejecuciones |
| max_iter | 1+ | 300 | Máximo de iteraciones |
| random_state | 0+ | 42 | Semilla aleatoria |

### Ventajas

✅ Rápido y eficiente para datasets grandes  
✅ Fácil de entender e implementar  
✅ Escalable a grandes dimensiones  
✅ Parámetros interpretables  

### Desventajas

❌ Requiere especificar K de antemano  
❌ Sensible a la inicialización  
❌ Asume clusters esféricos de tamaño similar  
❌ Sensible a outliers  
❌ No maneja bien datos con densidades variadas  

### Ejemplo de Uso

```bash
# Entrenar con K=3
curl -X POST http://localhost:5000/api/train/kmeans

# Ver resultados
curl http://localhost:5000/api/results/kmeans
```

### Casos de Uso

- Segmentación de clientes en marketing
- Análisis de comportamiento de usuarios
- Organización de documentos
- Compresión de imágenes

---

## 2. Hierarchical Clustering

### ¿Qué es Hierarchical Clustering?

Hierarchical Clustering es un método **aglomerativo** que construye una jerarquía de clusters mediante la combinación repetida de clusters más similares. Genera un dendrograma que visualiza las relaciones entre clusters.

### Algoritmo (Agglomerative)

1. **Inicio**: Cada punto es su propio cluster (N clusters para N puntos)

2. **Iteración**:
   - Encontrar los dos clusters más cercanos
   - Combinarlos en un nuevo cluster
   - Repetir hasta tener 1 cluster

3. **Resultado**: Dendrograma que puede cortarse a diferentes niveles para obtener distintos números de clusters

### Métodos de Enlace (Linkage)

El "enlace" define cómo se calcula la distancia entre clusters:

#### Ward (Recomendado)
- Minimiza la varianza dentro del cluster
- Produce clusters más compactos y esféricos
- Similar a K-means en resultados

```python
AgglomerativeClustering(linkage='ward')
```

#### Complete Linkage
- Usa la máxima distancia entre puntos de dos clusters
- Produce clusters más dispersos
- Sensible a outliers

```python
AgglomerativeClustering(linkage='complete')
```

#### Average Linkage
- Usa la distancia promedio entre puntos
- Equilibrio entre ward y complete
- Resultado intermedio

```python
AgglomerativeClustering(linkage='average')
```

#### Single Linkage
- Usa la mínima distancia entre puntos
- Tiende a formar clusters "encadenados"
- Menos recomendado para clusters bien separados

```python
AgglomerativeClustering(linkage='single')
```

### Implementación

```python
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler

# Normalizar datos
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Entrenar Hierarchical Clustering
hierarchical = AgglomerativeClustering(
    n_clusters=3,       # Número final de clusters
    linkage='ward'      # Método de enlace
)

labels = hierarchical.fit_predict(features_scaled)
```

### Parámetros Clave

| Parámetro | Rango | Defecto | Descripción |
|-----------|-------|---------|-------------|
| n_clusters | 2+ | 3 | Número final de clusters |
| linkage | ward, complete, average, single | ward | Método de enlace |

### Ventajas

✅ No requiere especificar K (cota el dendrograma)  
✅ Produce dendrograma informativo  
✅ Mejor para análisis exploratorio  
✅ Flexible: se puede obtener diferentes números de clusters  
✅ Determinista (no es aleatorio)  

### Desventajas

❌ Más lento que K-means (O(n²) a O(n³))  
❌ No es fácil de escalar a datasets muy grandes  
❌ Sensible a la selección del método de enlace  
❌ Decisiones de fusión son irreversibles  

### Ejemplo de Uso

```bash
# Entrenar con K=3, linkage='ward'
curl -X POST http://localhost:5000/api/train/hierarchical

# Ver resultados
curl http://localhost:5000/api/results/hierarchical
```

### Dendrograma

El dendrograma muestra la jerarquía de clusters. La altura de cada fusión indica la distancia entre clusters fusionados.

```
        ┌──────────┐
        │    C1   │
    ┌───┤         │
    │   │  ┌──────┘
  ┌─┴─┐ │  │
  │   │ │  │  ┌──────┐
  │ C2├─┤  └──┤ C2  │
  │   │ │     │      │
  └───┘ │     └──────┘
        │
        └──────────
```

### Casos de Uso

- Análisis de relaciones entre clusters
- Biología: clasificación de especies
- Marketing: análisis de segmentación jerárquica
- Análisis de documentos
- Estudios de filogenia

---

## 3. Comparación K-means vs. Hierarchical

| Aspecto | K-means | Hierarchical |
|---------|---------|--------------|
| **Velocidad** | Rápido (O(nkd)) | Lento (O(n²)) |
| **Especificar K** | Requerido | Opcional |
| **Determinismo** | No (estocástico) | Sí |
| **Escalabilidad** | Excelente | Moderada |
| **Interpretabilidad** | Buena | Excelente |
| **Visualización** | Scatter plot | Dendrograma |
| **Outliers** | Sensible | Sensible |
| **Clusters esféricos** | Sí | Flexible |

---

## 4. Métricas de Evaluación

### Silhouette Score

Mide qué tan similares son los puntos dentro de un cluster comparado con puntos en otros clusters.

**Fórmula**:
```
s(i) = (b(i) - a(i)) / max(a(i), b(i))
```

Donde:
- a(i) = distancia promedio a otros puntos en el mismo cluster
- b(i) = distancia promedio mínima a puntos en otros clusters

**Interpretación**:
- **-1**: Clasificación completamente incorrecta
- **0**: Clusters solapados
- **1**: Clusters bien separados

**Rango ideal**: > 0.5 (bueno), > 0.7 (excelente)

### Davies-Bouldin Index

Mide la compacidad y separación promedio de los clusters.

**Fórmula**:
```
DBI = (1/k) * Σ max(Di,j)
```

**Interpretación**:
- **Menor es mejor**
- 0 = clusters perfectamente separados
- Típicamente 0-3 para datos reales

### Calinski-Harabasz Index

Razón entre varianza inter-cluster e intra-cluster.

**Fórmula**:
```
CH = (SS_b / (k-1)) / (SS_w / (n-k))
```

**Interpretación**:
- **Mayor es mejor**
- Típicamente 0-1000+ para datos reales
- Mayor separación = índice más alto

### Inertia (solo K-means)

Suma de distancias cuadradas de puntos a su centroide más cercano.

**Fórmula**:
```
I = Σ min_j ||x_i - c_j||²
```

**Interpretación**:
- **Menor es mejor**
- Siempre disminuye con más clusters
- Útil para el método del codo

---

## 5. Métodos para Encontrar K Óptimo

### Método del Codo

Gráfico de inertia vs. número de clusters. El "codo" indica el K óptimo.

```python
inertias = []
k_range = range(1, 10)

for k in k_range:
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(features)
    inertias.append(kmeans.inertia_)

# El "codo" (cambio de pendiente) es el K óptimo
```

### Silhouette Analysis

Calcular silhouette score para diferentes K y elegir el mayor.

```python
silhouette_scores = []

for k in range(2, 10):
    kmeans = KMeans(n_clusters=k)
    labels = kmeans.fit_predict(features)
    score = silhouette_score(features, labels)
    silhouette_scores.append(score)

optimal_k = np.argmax(silhouette_scores) + 2
```

### Algoritmo Implementado

El endpoint `/api/train/auto-k` usa Silhouette Analysis:

```python
def _find_optimal_k(data, max_k=10):
    silhouette_scores = []
    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, ...)
        labels = kmeans.fit_predict(data)
        score = silhouette_score(data, labels)
        silhouette_scores.append(score)
    
    optimal_k = np.argmax(silhouette_scores) + 2
    return optimal_k
```

---

## 6. Normalización y Preprocesamiento

### StandardScaler

Normaliza features a media=0 y desviación estándar=1.

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)
```

**Por qué es importante**:
- K-means es sensible a la escala de features
- Un feature con rango 0-1000 domina sobre uno con rango 0-1
- La normalización equilibra la importancia de features

**Ejemplo**:
```
Feature 1: 0 - 1000    →  Normalizado: -2 a +2
Feature 2: 0 - 1       →  Normalizado: -2 a +2
```

---

## 7. Recomendaciones de Uso

### Usar K-means cuando:
- Tienes un dataset grande (>10,000 filas)
- Necesitas resultados rápidos
- Sabes aproximadamente cuántos clusters esperas
- Los clusters son aproximadamente esféricos

### Usar Hierarchical cuando:
- Quieres explorar la estructura jerárquica
- Tienes un dataset pequeño-mediano (<10,000)
- No sabes el número óptimo de clusters
- Necesitas visualizar el dendrograma

### Usar ambos cuando:
- Quieres comparar resultados
- Es un análisis exploratorio
- Los clusters no son obvios

---

## 8. Ejemplos Prácticos

### Ejemplo 1: Encontrar K óptimo

```python
# Cliente con frecuencia de compra baja
{
    "frecuencia_compra": 5,
    "monto_total_gastado": 1000,
    "monto_promedio_compra": 200,
    ...
}

# Cliente con alta frecuencia
{
    "frecuencia_compra": 100,
    "monto_total_gastado": 50000,
    "monto_promedio_compra": 500,
    ...
}
```

K-means los clasificaría en clusters diferentes por su comportamiento.

### Ejemplo 2: Interpretación de Resultados

Si Silhouette Score = 0.65:
- Buenos clusters, pero con algo de solapamiento
- Aceptable para segmentación de clientes
- Podrías intentar ajustar K o normalización

Si Davies-Bouldin Index = 0.45:
- Clusters bien definidos
- Muy separados y compactos
- Excelente para tomar decisiones

---

## 9. Troubleshooting

### Silhouette Score muy bajo (<0.3)

**Causas**:
- Demasiados/pocos clusters
- Features no normalizados
- Clusters naturales no existen

**Soluciones**:
- Cambiar K
- Usar StandardScaler
- Usar método del codo

### Clusters muy desbalanceados

**Causas**:
- K inapropiado
- Datos sesgados
- Outliers influyentes

**Soluciones**:
- Usar K-means con múltiples ejecuciones
- Remover outliers
- Usar pesos

### Resultados inconsistentes

**Causas** (K-means):
- Inicialización aleatoria
- Pocos n_init

**Soluciones**:
- Aumentar n_init
- Usar k-means++
- Fijar random_state

---

## Referencias

1. MacQueen, J. B. (1967). "Some Methods for Classification and Analysis of Multivariate Observations"
2. Ward, J. H. (1963). "Hierarchical Grouping to Optimize an Objective Function"
3. Rousseeuw, P. J. (1987). "Silhouettes: A graphical aid to the interpretation and validation of cluster analysis"
4. Davies, D. L.; Bouldin, D. W. (1979). "A Cluster Separation Measure"

---

**Versión**: 1.0  
**Última actualización**: Diciembre 2025
