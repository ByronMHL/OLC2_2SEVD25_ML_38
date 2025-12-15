import axios from 'axios'

const instance = axios.create({
    baseURL: 'http://localhost:5000/api',
});

// Verifica el estado del backend
export const health = async () => {
    try {
        const response = await instance.get('/health');
        return response.data; // { status: 'ok', service: 'studentguard-backend' }
    } catch (error) {
        throw error.response?.data || { error: 'Backend no disponible' };
    }
};

// Función para carga masiva de archivos CSV
export const cargaMasiva = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    
    try {
        // Endpoint correcto según backend: POST /api/upload
        const response = await instance.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

// Limpieza de datos
export const clean = async () => {
    try {
        const response = await instance.get('/clean');
        return response.data; // { message: "Se han limpiado los datos correctamente" }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

// Entrenamiento del modelo
export const train = async () => {
    try {
        const response = await instance.get('/training');
        return response.data; // { message, metadata, metrics, results }
    } catch (error) {
        // Propagar el mensaje del backend (por ejemplo: "Primero ejecute la limpieza de datos (/clean)")
        throw error.response?.data || error.message;
    }
};

// Reentrenamiento con hiperparámetros
// RandomizedSearchCV (POST con parámetros ajustables)
export const randomSearch = async (params) => {
    try {
        const response = await instance.post('/training/randomsearch', params);
        return response.data; // { message, best_params, best_score_cv, metrics, results }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

// Predicción con nuevos datos
export const predict = async (inputData) => {
    try {
        const response = await instance.post('/predict', inputData);
        return response.data; // { predictions: [...] }
    } catch (error) {
        throw error.response?.data || error.message;
    }   
};
