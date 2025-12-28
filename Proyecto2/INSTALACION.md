# Instrucciones de Ejecución

## Requisitos del Sistema

- **Python**: 3.7 o superior
- **Pip**: Gestor de paquetes de Python
- **RAM**: Mínimo 2GB para datasets medianos
- **Almacenamiento**: Mínimo 500MB para dependencias

## Instalación Paso a Paso

### Paso 1: Verificar Python

```bash
python --version
pip --version
```

Deberías ver versiones de Python 3.7+ y pip.

### Paso 2: Navegar al Directorio del Backend

```bash
cd Proyecto2/Backend
```

### Paso 3: Crear Entorno Virtual (Recomendado)

#### En Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### En Windows (CMD):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### En macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### Paso 4: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- Flask 3.0.0
- pandas 2.2.3
- scikit-learn 1.4.2
- numpy 1.24.3
- python-dotenv 1.0.1
- flask-cors 4.0.0

### Paso 5: Verificar Instalación

```bash
pip list
```

Deberías ver las dependencias listadas.

---

## Ejecutar el Backend

### Ejecución Normal

```bash
python main.py
```

Deberías ver:
```
 * Serving Flask app 'main'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

El servidor está listo cuando veas el mensaje anterior.

### Ejecución en Modo Debug

Ya viene por defecto. Para desactivarlo, edita `main.py`:

```python
app.run(host="0.0.0.0", port=5000, debug=False)
```

### Cambiar Puerto

Si el puerto 5000 está en uso, edita `main.py`:

```python
app.run(host="0.0.0.0", port=5001, debug=True)  # Cambiar a 5001
```

---

## Verificar que el Servidor Funciona

### Opción 1: Navegador

Abre en tu navegador:
```
http://localhost:5000/api/health
```

Deberías ver:
```json
{"status": "ok", "service": "customer-segmentation-backend"}
```

### Opción 2: cURL

```bash
curl http://localhost:5000/api/health
```

### Opción 3: PowerShell (Windows)

```powershell
Invoke-WebRequest http://localhost:5000/api/health
```

---

## Ejecutar Suite de Pruebas

### Instalar Dependencia de Pruebas

```bash
pip install requests
```

### Ejecutar Todas las Pruebas

```bash
python test_api.py
```

### Ejecutar Prueba Específica

```bash
python test_api.py health          # Solo health check
python test_api.py upload          # Solo carga
python test_api.py clean           # Solo limpieza
python test_api.py kmeans          # Solo K-means
python test_api.py results         # Solo resultados
```

### Interpreter la Salida

```
✅ PASÓ        - Test completado exitosamente
❌ FALLÓ       - Test no pasó la validación
❌ ERROR      - Error en la ejecución
```

---

## Flujo Completo de Ejecución

### Paso 1: Iniciar el Servidor

Terminal 1:
```bash
cd Proyecto2/Backend
python main.py
```

### Paso 2: Ejecutar Pruebas en Otra Terminal

Terminal 2:
```bash
cd Proyecto2/Backend
python test_api.py
```

O pruebas individuales:

```bash
# Cargar datos
curl -X POST -F "file=@../data/data_prueba_proyecto2.csv" http://localhost:5000/api/upload

# Limpiar
curl http://localhost:5000/api/clean

# Entrenar K-means
curl -X POST http://localhost:5000/api/train/kmeans

# Ver resultados
curl http://localhost:5000/api/results/kmeans
```

---

## Archivos Generados

El sistema no crea archivos locales por defecto (almacenamiento en memoria). Para cambiar esto, modifica `controllers/upload.py` para guardar CSVs en la carpeta `data/raw/`.

---

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'flask'"

**Solución**:
```bash
pip install -r requirements.txt
```

### Error: "Address already in use"

**Problema**: El puerto 5000 ya está en uso

**Solución 1**: Cambiar puerto en `main.py`
```python
app.run(host="0.0.0.0", port=5001, debug=True)
```

**Solución 2**: Encontrar qué usa el puerto
```bash
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # macOS/Linux
```

Luego terminar ese proceso.

### Error: "No module named 'sklearn'"

**Solución**:
```bash
pip install scikit-learn==1.4.2
```

### Error: "No se ha cargado ningún archivo"

**Problema**: No ejecutaste `POST /api/upload` primero

**Solución**: Cargar el CSV
```bash
curl -X POST -F "file=@../data/data_prueba_proyecto2.csv" http://localhost:5000/api/upload
```

### Error: "Los datos no han sido preprocesados"

**Problema**: No ejecutaste `GET /api/clean` después de cargar

**Solución**: Ejecutar limpieza
```bash
curl http://localhost:5000/api/clean
```

### Error: "El modelo no ha sido entrenado"

**Problema**: Intentaste obtener resultados sin entrenar primero

**Solución**: Entrenar modelo
```bash
curl -X POST http://localhost:5000/api/train/kmeans
```

### Error: "ConnectionRefusedError"

**Problema**: El servidor no está corriendo

**Solución**: Inicia el servidor
```bash
python main.py
```

### Error: "JSONDecodeError"

**Problema**: Respuesta no es JSON válido

**Solución**: Verificar que el servidor está corriendo correctamente
```bash
curl http://localhost:5000/api/health
```

---

## Desarrollo Futuro

### Para agregar nuevos endpoints:

1. Crear archivo en `controllers/nuevo_controller.py`
2. Crear blueprint en ese archivo
3. Registrarlo en `main.py`:
   ```python
   from controllers.nuevo_controller import nuevo_bp
   app.register_blueprint(nuevo_bp, url_prefix="/api")
   ```

### Para agregar nuevos algoritmos:

1. Implementar en `training.py`
2. Agregar al `ModelStore` en `models.py`
3. Crear endpoints correspondientes

### Para modificar limpieza:

Editar `controllers/clean.py` en la función `clean_data()`

---

## Desactivar Entorno Virtual

Cuando termines de trabajar:

```bash
deactivate
```

---

## Próximas Sesiones

Para trabajar de nuevo:

### Windows:
```powershell
cd Proyecto2/Backend
.\venv\Scripts\Activate.ps1
python main.py
```

### macOS/Linux:
```bash
cd Proyecto2/Backend
source venv/bin/activate
python main.py
```

---

## Recursos Adicionales

- **Documentación de API**: Ver `Backend/readme.md`
- **Algoritmos**: Ver `ALGORITMOS.md`
- **Inicio Rápido**: Ver `QUICKSTART.md`
- **Sklearn**: https://scikit-learn.org/
- **Flask**: https://flask.palletsprojects.com/
- **Pandas**: https://pandas.pydata.org/

---

## Contacto y Soporte

Para preguntas sobre ejecución, consultar documentación o reportar bugs:
- Revisar archivo correspondiente (`readme.md`, `QUICKSTART.md`, `ALGORITMOS.md`)
- Verificar soluciones en esta sección
- Contactar al equipo de desarrollo

---

**Versión**: 1.0  
**Última actualización**: Diciembre 2025
