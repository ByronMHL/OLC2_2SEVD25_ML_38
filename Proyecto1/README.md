# OLC2_2SEVD25_ML_38

# Backend StudentGuard 

## Descripción General
API para cargar archivos CSV, limpiar datos, entrenar un modelo de Machine Learning para predecir riesgo de desercion académica en estudiantes, y realizar predicciones individuales. Utiliza Flask como framework web y scikit-learn para el procesamiento y modelado.

## Endpoints Principales
- `GET /api/health`: Verifica el estado del servicio.
- `POST /api/upload`: Recibe un archivo CSV y valida columnas requeridas.
- `GET /api/clean`: Limpia los datos cargados.
- `GET /api/training`: Entrena el modelo con parámetros personalizados.
- `POST /api/training/randomsearch`: Realiza ajuste de hiperparámetros con RandomizedSearchCV.
- `POST /api/predict`: Predice riesgo de desercion para un estudiante individual dada las notas, promedio de evaluaciones, etc.

Columnas requeridas en el CSV: `promedio_actual`, `asistencia_clases`, `tareas_entregadas`, `participacion_clase`, `horas_estudio`, `promedio_evaluaciones`, `cursos_reprobados`, `actividades_extracurriculares`, `reportes_disciplinarios`, `riesgo`.

## 1. Modelo Utilizado
Se emplea **Random Forest Classifier** de scikit-learn para la predicción de desercion académica (binario: 0 = no riesgo, 1 = riesgo). Se tomo en consideracion por los siguientes aspectos:

- Es robusto ante outliers y valores faltantes (después de la limpieza).
- Proporciona importancia de características, útil para interpretar factores de riesgo como asistencia o evaluaciones.
- Ofrece probabilidades de predicción, permitiendo umbrales ajustables para decisiones.
## 2. Limpieza de Datos en `clean.py`
El proceso de limpieza prepara el dataset para modelado:

- **Eliminación de columnas irrelevantes**: Se eliminó `carnet`, `first_name`, `last_name`, `gender` (no aportan al riesgo académico).
- **Eliminación de duplicados**: Remueve filas idénticas para evitar sesgos.
- **Conversión de tipos**: Convierte columnas numéricas a tipos apropiados (int32/float32), manejando errores.
- **Procesamiento de `actividades_extracurriculares`**: Evalúa strings a listas, reemplaza vacías con `['n/a']` para codificación binaria posterior.
- **Codificación de la columnba objetivo`riesgo`**: Mapea "no riesgo" a 0, "riesgo" a 1.
- **Imputación de valores faltantes**: Para valores 0 en numéricas, usa mediana (para enteros) o media (para flotantes) para preservar distribuciones.

Esto asegura datos íntegros, sin nulos, y listos para preprocesamiento (escalado y binarización).

## 3. Hiperparámetros (Entrenamiento)
En el entrenamiento básico, se usan parámetros fijos para el Random Forest:

- `n_estimators=700`: Se consideró esta cantidad para equilibrar el tiempo de entrenamiento y capturar el problema.
- `class-weight=balanced`: Se consideró para mantener el balance entre riesgo y no riesgo, asegurando la minoria.
- `max_depth=15`: Se consideró para evitar sobreajuste y que el modelo obtenga patrones estrictamente del entrenamiento.
- `random_state=42`: Semilla para reproducibilidad de resultados.

Estos valores son conservadores para asegurar consistencia sin optimización excesiva, priorizando simplicidad en el flujo básico.

## 4. Hiperparámetros (Ajustable)
El ajuste se realiza con `RandomizedSearchCV` para optimizar el modelo. Parámetros ajustables desde la interfaz de usuario:

- `n_iter`: Número de combinaciones a probar (1-200, recomendado 10-50). Controla exhaustividad de la búsqueda.
- `cv`: Número de folds en validación cruzada (2-10, recomendado 3-5). Evalúa generalización.

Espacio de búsqueda fijo para estabilidad:
- `classifier__n_estimators`: [100, 300, 500, 800, 1000] – Más árboles mejoran precisión.
- `classifier__max_depth`: [10, 20, 30, 40, 50] – Profundidad máxima para controlar complejidad.
- `classifier__min_samples_split`: [2, 5, 10] – Mínimo de muestras para dividir nodos.
- `classifier__min_samples_leaf`: [1, 2] – Mínimo de muestras en hojas.
- `classifier__bootstrap`: [True] – Usa muestreo con reemplazo.
- `classifier__max_features`: ["sqrt", "log2"] – Número de características por árbol.

Se optimiza por métrica F1 para balancear precisión y recall en clases desbalanceadas. RandomizedSearchCV es eficiente para espacios grandes, evitando GridSearchCV por tiempo.



## Instalación y Ejecución
1. Crear entorno virtual (opcional).
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Ejecutar: `python main.py`.

## Pruebas con Postman
- **Upload**: POST a `/api/upload`, body form-data con key `file`.
- Respuesta exitosa: JSON con mensaje, ruta, filas y columnas.

Errores comunes: 400 por columnas faltantes o formato inválido.