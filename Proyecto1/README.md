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
- **Eliminación de duplicados**: Se removieron filas idénticas para evitar sesgos.
- **Conversión de tipos**: columnas numéricas a tipos apropiados (int32/float32), manejando errores.
- **Procesamiento de `actividades_extracurriculares`**: Conversion de strings a listas, asi como reemplazar listas vacías con el elemento `['n/a']` para codificación binaria posterior.
- **Codificación de la columnba objetivo`riesgo`**: Se mapeó "no riesgo" a 0, "riesgo" a 1.
- **Imputación de valores faltantes**: Para valores 0 en numéricas, se utilizó mediana (para enteros) y media (para flotantes) para preservar distribuciones.

Se busca asegurar datos, sin nulos, y listos para preprocesamiento (escalado y binarización).

## 3. Hiperparámetros (Entrenamiento)
En el entrenamiento básico, se usan parámetros fijos para el Random Forest:

- `n_estimators=700`: Se consideró esta cantidad para equilibrar el tiempo de entrenamiento y capturar el problema.
- `class-weight=balanced`: Se consideró para mantener el balance entre riesgo y no riesgo, asegurando la minoria.
- `max_depth=15`: Se consideró para evitar sobreajuste y que el modelo obtenga patrones estrictamente del entrenamiento.
- `random_state=42`: Semilla para reproducibilidad de resultados.

Estos valores son conservadores para asegurar consistencia sin optimización excesiva, priorizando simplicidad en el flujo básico.

## 4. Hiperparámetros (Ajustable)
### 4.1. ¿Qué es RandomizedSearchCV?

RandomizedSearchCV no es un modelo de Machine Learning, sino un método de optimización de hiperparámetros proporcionado por scikit-learn.

Su función principal es:
``` 
Probar distintas combinaciones de hiperparámetros de un modelo 
y seleccionar aquella que produce el mejor desempeño según una 
métrica definida.
```
En este proyecto, RandomizedSearchCV se utiliza para optimizar un modelo Random Forest, evaluando automáticamente diferentes configuraciones del bosque de árboles.

### 4.2. Relación entre RandomizedSearchCV y Random Forest

En la arquitectura implementada:

- RandomForestClassifier
Es el modelo predictivo, encargado de aprender patrones y realizar predicciones.

- RandomizedSearchCV
Es el optimizador, que envuelve al modelo y prueba múltiples configuraciones de hiperparámetros.

Esto se logra mediante un Pipeline, donde RandomizedSearchCV ajusta los parámetros del clasificador identificado por el prefijo classifier__.
```python
Pipeline(steps=[
    ("preprocessor", preproc),
    ("classifier", RandomForestClassifier())
])
```
De esta forma:
- El preprocesamiento
- El modelo
- Y la búsqueda de hiperparámetros

quedan integrados en un solo flujo reproducible.

### 4.3. ¿Qué hace exactamente RandomizedSearchCV en este proyecto?

- En este sistema, RandomizedSearchCV:
- Recibe un espacio de búsqueda de hiperparámetros (param_distributions)
- Selecciona aleatoriamente combinaciones de esos parámetros
- Entrena el modelo con cada combinación
- Evalúa cada entrenamiento usando validación cruzada (Cross-Validation)
- Calcula la métrica F1-score
- Selecciona automáticamente la mejor configuración
- Devuelve el modelo optimizado (best_estimator_)

### 4.4. Espacio de búsqueda definido
El espacio de hiperparámetros utilizado es:
```python
param_dist = {
    "classifier__n_estimators": [100, 300, 500, 800, 1000],
    "classifier__max_depth": [10, 20, 30, 40, 50],
    "classifier__min_samples_split": [2, 5, 10],
    "classifier__min_samples_leaf": [1, 2],
    "classifier__bootstrap": [True],
    "classifier__max_features": ["sqrt", "log2"],
}
```
#### Significado de los principales hiperparámetros 

- n_estimators
Número de árboles en el bosque. Más árboles suelen mejorar la generalización, a costa de mayor tiempo de entrenamiento.

- max_depth
Profundidad máxima de cada árbol. Controla el sobreajuste.

- min_samples_split
Mínimo de muestras necesarias para dividir un nodo interno.

- min_samples_leaf
Mínimo de muestras que debe contener una hoja. Ayuda a estabilizar el modelo.

- max_features
Número de variables consideradas en cada división del árbol, fomentando diversidad entre árboles.
### 4.5. ¿Por qué se eligió RandomizedSearchCV?

La decisión de usar RandomizedSearchCV en lugar de GridSearchCV se basa en las siguientes razones:

- Eficiencia computacional
    - No evalúa todas las combinaciones posibles
    - Reduce significativamente el tiempo de entrenamiento

- Escalabilidad
    - Permite explorar espacios de hiperparámetros más amplios
    - Se adapta mejor a datasets de tamaño medio

- Práctica común en la industria
    - En entornos reales se prioriza eficiencia

- Control desde el frontend
    El sistema permite ajustar únicamente:
    - n_iter: número de combinaciones probadas
    - cv: número de particiones de validación cruzada

Esto brinda flexibilidad sin comprometer la estabilidad del modelo.

### 4.6. Métrica de optimización utilizada
```python
scoring="f1"
```
Se seleccionó F1-score como métrica principal porque:
- El problema presenta clases desbalanceadas
- Es más importante detectar correctamente estudiantes en riesgo
- Equilibra precisión y recall

Esto garantiza un modelo más útil para el objetivo del sistema.

### 4.7. Validación cruzada (Cross-Validation)
```python
cv = 3
```
La validación cruzada permite:
- Evaluar el modelo en distintos subconjuntos del dataset
- Reducir la dependencia de una sola partición
- Obtener un desempeño más robusto

Los valores de cv se mantienen en rangos seguros (2–10) para evitar sobrecostos computacionales.

### 4.8. Persistencia del modelo optimizado
Una vez finalizada la búsqueda, el mejor pipeline se guarda automáticamente:
```python
joblib.dump(best_pipeline, model_path)
```
Esto permite:
- Reutilizar el modelo para predicciones
- Garantizar consistencia entre entrenamiento y predicción
- Evitar reentrenamientos innecesarios

El pipeline persistido incluye:
- Preprocesamiento
- Codificación
- Modelo Random Forest optimizado

### 4.10. Resumen final
Random Forest es el modelo predictivo
RandomizedSearchCV optimiza sus hiperparámetros
El pipeline garantiza consistencia y evita fugas de información
Se prioriza eficiencia, escalabilidad y robustez

El modelo Random Forest fue optimizado utilizando RandomizedSearchCV, debido a su eficiencia para explorar espacios amplios de hiperparámetros con un menor costo computacional, priorizando el F1-score como métrica principal dada la naturaleza desbalanceada del problema.

## 5. Módulo de predicción del modelo
### 5.1 Objetivo del módulo
El módulo de predicción tiene como objetivo realizar inferencias individuales sobre el riesgo académico de un estudiante, utilizando un modelo de aprendizaje automático previamente entrenado y persistido.
Este módulo garantiza que los datos de entrada sean procesados bajo las mismas transformaciones aplicadas durante el entrenamiento, asegurando consistencia, confiabilidad y reproducibilidad en los resultados.

### 5.2 Flujo general de la predicción

El flujo del proceso de predicción se compone de las siguientes etapas:
- Recepción y validación de los datos de entrada.
- Carga del modelo entrenado desde disco.
- Inspección del preprocesador contenido en el pipeline.
- Transformación de los datos de entrada.
- Generación de la predicción y probabilidad asociada.
- Retorno de resultados al cliente.

Cada una de estas etapas se describe a continuación.

### 5.3 Validación de los datos de entrada

El endpoint /predict recibe un objeto JSON desde el frontend que contiene la información académica del estudiante.
Antes de realizar cualquier predicción, el sistema valida que todos los campos requeridos estén presentes, tales como:
- Promedio actual
- Asistencia a clases
- Tareas entregadas
- participacion en clase
- Horas de estudio
- promedio de evaluaciones
- Cursos reprobados
- Actividades extracurriculares
- Reportes disciplinarios

Esta validación es necesaria para evitar predicciones con información incompleta o inconsistente, ya que el modelo fue entrenado con un conjunto fijo de variables.

### 5.4 Carga del modelo entrenado

El sistema intenta cargar un pipeline previamente persistido en formato .pkl, priorizando el modelo entrenado mediante búsqueda de hiperparámetros (pipeline_hyper.pkl).
En caso de no existir, se utiliza un modelo de entrenamiento estándar (pipeline_training.pkl).

Si no se encuentra ningún modelo entrenado, el sistema retorna un error indicando que es necesario ejecutar previamente el proceso de entrenamiento.

Este enfoque garantiza que el proceso de predicción solo se ejecute cuando existe un modelo válido.

### 5.5 Uso del pipeline completo

El modelo cargado corresponde a un Pipeline de Scikit-learn, el cual encapsula tanto el preprocesamiento como el clasificador final.

El pipeline incluye:
- Escalado de variables numéricas mediante StandardScaler.
- Codificación binaria de las actividades extracurriculares.
- El modelo RandomForestClassifier.

Utilizar el pipeline completo permite asegurar que los datos de entrada sean transformados de manera idéntica a los datos utilizados durante el entrenamiento, evitando errores comunes en sistemas de predicción.

### 5.6 Inspección dinámica de columnas

El sistema inspecciona dinámicamente el preprocesador del pipeline para identificar:
- Columnas numéricas esperadas.
- Columnas binarias correspondientes a actividades extracurriculares.

Este enfoque evita el uso de columnas definidas manualmente (hardcoded) y permite que el módulo de predicción se adapte automáticamente a cambios futuros en el modelo entrenado.

### 5.7 Codificación de actividades extracurriculares

Las actividades extracurriculares se reciben como una lista de valores categóricos.
Para que el modelo pueda procesarlas, se convierten en una representación binaria consistente con la utilizada durante el entrenamiento.

Cada actividad conocida por el modelo se representa con:
- 1 si el estudiante participa en ella.
- 0 si no participa.

Las actividades no contempladas durante el entrenamiento no afectan la predicción.

### 5.8 Construcción de la instancia de entrada

Una vez procesados los datos, se construye un DataFrame con una sola fila que contiene:
- Variables numéricas escaladas.
- Variables binarias codificadas.
- Mismo orden y nombres de columnas que el modelo espera.

Este paso es fundamental para cumplir con los requerimientos de Scikit-learn durante la inferencia.

### 5.9 Generación de la predicción

El modelo realiza dos tipos de inferencia:
- Predicción de clase (predict): indica si el estudiante presenta riesgo académico (0 o 1).

- Predicción de probabilidad (predict_proba): indica la probabilidad estimada de que el estudiante se encuentre en riesgo.

La probabilidad permite una interpretación más detallada del resultado, facilitando la toma de decisiones académicas.

### 5.10 Respuesta al cliente

El sistema retorna una respuesta en formato JSON que incluye:
- La predicción final del riesgo.
- La probabilidad asociada.
- Los datos utilizados como entrada para la predicción.

Esto permite trazabilidad, auditoría y validación de los resultados obtenidos.

### 5.11 Consideraciones finales

El diseño del módulo de predicción sigue buenas prácticas de ingeniería de aprendizaje automático, asegurando:
- Consistencia entre entrenamiento y predicción.
- Robustez ante cambios en el modelo.
- Validación estricta de datos.
- Interpretabilidad de los resultados.

Este enfoque garantiza que las predicciones generadas sean confiables y reproducibles dentro del sistema.


## Instalación y Ejecución
1. Crear entorno virtual (opcional).
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Ejecutar: `python main.py`.
4. 

## Frontend: Inicio y Dependencias
- Ubicación: Proyecto1/Frontend
- Stack: React + Vite + TailwindCSS
- Gestor de paquetes: npm

### Requisitos previos
- Node.js LTS (recomendado 18+)
- npm 9+

### Instalación
1. En la carpeta del frontend:

    ```powershell
    cd "C:\Users\USUARIO\Documents\Repositorios\OLC2_2SEVD25_ML_38\Proyecto1\Frontend"
    npm install
    ```

### Ejecución en desarrollo
```powershell
npm run dev
```
Vite levanta el servidor en `http://localhost:5173/` por defecto.

### Build de producción
```powershell
npm run build
npm run preview
```

### Principales dependencias
- React y ReactDOM: UI y renderizado.
- Vite: bundler y dev server rápido.
- TailwindCSS + PostCSS + Autoprefixer: estilos utilitarios.
- Axios: comunicación HTTP con el backend.
- ESLint: linting del código.

Se instalan automáticamente con `npm install` según el `package.json`.

### Funcionalidades del frontend
- Páginas: Ajuste (RandomizedSearchCV), Evaluación (métricas de entrenamiento), Predicción (inferencia individual).
- Layout: `DashboardLayout.jsx` y `Sidebar.jsx` para navegación.
- Servicios: `service/Conexion/ComunicacionBack.js` y `service/Service.js` para llamadas a `/api/health`, `/api/upload`, `/api/clean`, `/api/training`, `/api/training/randomsearch`, `/api/predict`.
- Estado y UI: componentes React con hooks, estilos Tailwind, validaciones de inputs y visualización de resultados (colores, barra de probabilidad, iconos).
- Configuración: `vite.config.js`, `tailwind.config.ts`, `postcss.config.js`, `eslint.config.js`.

Si `npm run dev` falla, verifica versión de Node, reinstala dependencias y revisa cambios recientes en `src/`.

## Pruebas con Postman
- **Upload**: POST a `/api/upload`, body form-data con key `file`.
- Respuesta exitosa: JSON con mensaje, ruta, filas y columnas.

Errores comunes: 400 por columnas faltantes o formato inválido.
