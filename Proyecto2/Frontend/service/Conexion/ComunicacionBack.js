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

// ------------------ Hyperparameters (configuración) ------------------
export const getKMeansParams = async () => {
    try {
        const response = await instance.get('/hyperparameters/kmeans');
        return response.data; // { algorithm, parameters }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const setKMeansParams = async (params) => {
    try {
        const response = await instance.post('/hyperparameters/kmeans', params);
        return response.data; // { success, parameters }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const getHierarchicalParams = async () => {
    try {
        const response = await instance.get('/hyperparameters/hierarchical');
        return response.data; // { algorithm, parameters }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const setHierarchicalParams = async (params) => {
    try {
        const response = await instance.post('/hyperparameters/hierarchical', params);
        return response.data; // { success, parameters }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const getAllHyperparams = async () => {
    try {
        const response = await instance.get('/hyperparameters/all');
        return response.data; // { kmeans, hierarchical, notes }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

// ------------------ Entrenamiento (training) ------------------
export const trainKMeans = async () => {
    try {
        const response = await instance.post('/train/kmeans');
        return response.data; // { success, metrics, ... }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const trainHierarchical = async () => {
    try {
        const response = await instance.post('/train/hierarchical');
        return response.data; // { success, metrics, ... }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const trainAutoK = async () => {
    try {
        const response = await instance.post('/train/auto-k');
        return response.data; // { success, metrics, ... }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const getModelsStatus = async () => {
    try {
        const response = await instance.get('/models/status');
        return response.data; // status de modelos
    } catch (error) {
        throw error.response?.data || error.message;
    }
};
