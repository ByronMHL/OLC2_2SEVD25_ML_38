Backend StudentGuard - API de Upload

Endpoints:
- GET /api/health: Verifica el estado del servicio.
- POST /api/upload: Recibe un archivo CSV y valida columnas requeridas.

Columnas requeridas (según Readme del proyecto):
promedio_actual, asistencia_clases, tareas_entregadas, participacion_clase, horas_estudio, promedio_evaluaciones, cursos_reprobados, actividades_extracurriculares, reportes_disciplinarios, riesgo

Cómo ejecutar:
1. Crear y activar entorno virtual (opcional).
2. Instalar dependencias:
   pip install -r requirements.txt
3. Ejecutar el servidor:
   python main.py

Probar en Postman:
- Método: POST
- URL: http://localhost:5000/api/upload
- Body: form-data, key: file (tipo File), valor: seleccionar CSV.

Respuesta exitosa (200):
{
  "message": "Archivo CSV recibido y validado",
  "saved_to": "ruta",
  "rows": 100,
  "columns": ["..."],
  "extra_columns": ["..."]
}

Errores comunes:
- 400 Nombre de archivo vacío o faltan columnas requeridas.
- 400 Formato inválido (no CSV) o CSV no legible.

