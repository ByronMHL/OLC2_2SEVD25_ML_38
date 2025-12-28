# Guía de Inicio Rápido

## Requisitos Previos

- Python 3.7+
- pip (gestor de paquetes de Python)

## Instalación

### 1. Instalar dependencias

```bash
cd Proyecto2/Backend
pip install -r requirements.txt
```

### 2. Iniciar el servidor

```bash
python main.py
```

Deberías ver:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

## Uso Rápido

### Opción 1: Usando cURL (línea de comandos)

**1. Cargar datos:**
```bash
curl -X POST -F "file=@../data/data_prueba_proyecto2.csv" http://localhost:5000/api/upload
```

**2. Limpiar datos:**
```bash
curl http://localhost:5000/api/clean
```

**3. Entrenar K-means:**
```bash
curl -X POST http://localhost:5000/api/train/kmeans
```

**4. Ver resultados:**
```bash
curl http://localhost:5000/api/results/kmeans
```

### Opción 2: Usando Python (test_api.py)

**Ejecutar todas las pruebas:**
```bash
pip install requests
python test_api.py
```

**Ejecutar una prueba específica:**
```bash
python test_api.py health
python test_api.py upload
python test_api.py clean
python test_api.py kmeans
python test_api.py results
python test_api.py predict
```

### Opción 3: Usando Postman

1. Abrir Postman
2. Crear nueva request
3. Seleccionar método (GET, POST)
4. Ingresar URL: `http://localhost:5000/api/[endpoint]`
5. Configurar datos si es necesario
6. Enviar

## Flujo Típico de Trabajo

```
┌─────────────────────────────────────┐
│ 1. Cargar CSV (upload)              │
│    POST /api/upload                 │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 2. Limpiar datos (clean)            │
│    GET /api/clean                   │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 3. (Opcional) Configurar parámetros │
│    POST /api/hyperparameters/*      │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 4. Entrenar modelos                 │
│    POST /api/train/kmeans           │
│    POST /api/train/hierarchical     │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 5. Obtener resultados               │
│    GET /api/results/kmeans          │
│    GET /api/results/hierarchical    │
│    GET /api/results/comparison      │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 6. Hacer predicciones (nuevo datos) │
│    POST /api/predict/kmeans         │
└─────────────────────────────────────┘
```

## Ejemplos de Uso

### Ejemplo 1: Segmentación Básica

```bash
# 1. Cargar datos
curl -X POST -F "file=@../data/data_prueba_proyecto2.csv" http://localhost:5000/api/upload

# 2. Limpiar
curl http://localhost:5000/api/clean

# 3. Entrenar K-means con K=4
curl -X POST -H "Content-Type: application/json" \
  -d '{"n_clusters": 4}' \
  http://localhost:5000/api/hyperparameters/kmeans

curl -X POST http://localhost:5000/api/train/kmeans

# 4. Ver resultados
curl http://localhost:5000/api/results/kmeans | python -m json.tool
```

### Ejemplo 2: Comparar dos algoritmos

```bash
# 1. Cargar y limpiar
curl -X POST -F "file=@../data/data_prueba_proyecto2.csv" http://localhost:5000/api/upload
curl http://localhost:5000/api/clean

# 2. Entrenar ambos modelos
curl -X POST http://localhost:5000/api/train/kmeans
curl -X POST http://localhost:5000/api/train/hierarchical

# 3. Comparar resultados
curl http://localhost:5000/api/results/comparison | python -m json.tool
```

### Ejemplo 3: Encontrar K óptimo

```bash
# 1. Cargar y limpiar
curl -X POST -F "file=@../data/data_prueba_proyecto2.csv" http://localhost:5000/api/upload
curl http://localhost:5000/api/clean

# 2. Entrenar con K automático
curl -X POST http://localhost:5000/api/train/auto-k

# 3. Ver parámetros (incluye K automático encontrado)
curl http://localhost:5000/api/hyperparameters/kmeans
```

### Ejemplo 4: Predicción de nuevos clientes

```bash
# Primero, entrenar el modelo:
curl -X POST http://localhost:5000/api/train/kmeans

# Luego, hacer predicción:
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "frecuencia_compra": 50,
        "monto_total_gastado": 10000,
        "monto_promedio_compra": 200,
        "dias_desde_ultima_compra": 20,
        "antiguedad_cliente_meses": 36,
        "numero_productos_distintos": 25,
        "canal_encoded": 1
      }
    ]
  }' \
  http://localhost:5000/api/predict/kmeans | python -m json.tool
```

## Estructura de Datos

### Variables de Entrada

| Campo | Tipo | Rango | Ejemplo |
|-------|------|-------|---------|
| cliente_id | int | >0 | 1 |
| frecuencia_compra | float | ≥0 | 45.0 |
| monto_total_gastado | float | ≥0 | 10000.50 |
| monto_promedio_compra | float | ≥0 | 200.25 |
| dias_desde_ultima_compra | float | ≥0 | 30.0 |
| antiguedad_cliente_meses | float | ≥0 | 24.0 |
| numero_productos_distintos | float | ≥0 | 15.0 |
| canal_principal | string | variable | "web", "móvil", "tienda física" |
| producto_categoria | string | variable | "ropa", "electronica", "alimentos" |

### Respuestas de Éxito (200 OK)

Todas las respuestas exitosas tienen la estructura:
```json
{
  "success": true,
  "message": "Descripción de lo que pasó",
  "data": {...}
}
```

### Respuestas de Error

- **400 Bad Request**: Datos inválidos o incompletos
- **500 Internal Server Error**: Error en el servidor

## Solución de Problemas

### Error: "No se encontró el módulo"

```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error: "Puerto 5000 en uso"

```bash
# Cambiar puerto en main.py
# Línea: app.run(host="0.0.0.0", port=5001, debug=True)
```

### Error: "No se ha cargado ningún archivo"

```bash
# Asegúrate de cargar el CSV primero:
curl -X POST -F "file=@../data/data_prueba_proyecto2.csv" http://localhost:5000/api/upload
```

### Error: "Los datos no han sido preprocesados"

```bash
# Ejecuta primero la limpieza:
curl http://localhost:5000/api/clean
```

## Parámetros Recomendados

### Para datasets pequeños (<1000 registros):
```json
{
  "n_clusters": 3,
  "init": "k-means++",
  "n_init": 15,
  "max_iter": 500
}
```

### Para datasets medianos (1000-10000):
```json
{
  "n_clusters": 5,
  "init": "k-means++",
  "n_init": 10,
  "max_iter": 300
}
```

### Para datasets grandes (>10000):
```json
{
  "n_clusters": 8,
  "init": "k-means++",
  "n_init": 5,
  "max_iter": 200
}
```

## Documentación Completa

Para una documentación detallada de todos los endpoints, ver: `readme.md`

## Soporte

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.
