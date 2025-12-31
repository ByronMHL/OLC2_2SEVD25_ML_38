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
        // Ejecuta limpieza numérica y textual en una sola llamada
        const response = await instance.get('/clean-all');
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
        return response.data; // { kmeans, hierarchical, text_kmeans, notes }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const getTextKMeansParams = async () => {
    try {
        const response = await instance.get('/hyperparameters/text_kmeans');
        return response.data; // { algorithm, parameters }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const setTextKMeansParams = async (params) => {
    try {
        const response = await instance.post('/hyperparameters/text_kmeans', params);
        return response.data; // { success, parameters }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

// ------------------ Entrenamiento (training) ------------------
export const trainKMeans = async () => {
    try {
        const response = await instance.get('/training/kmeans');
        return response.data; // { success, metrics, ... }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const trainHierarchical = async () => {
    try {
        const response = await instance.get('/training/hierarchical');
        return response.data; // { success, metrics, ... }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const trainAutoK = async () => {
    try {
        const response = await instance.get('/training/auto-k');
        return response.data; // { success, metrics, ... }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const trainTextKMeans = async () => {
    try {
        const response = await instance.get('/training/text/kmeans');
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

// ------------------ Reportes ------------------
export const getNumericProfile = async (clusterCol) => {
    try {
        const params = clusterCol ? { cluster_col: clusterCol } : {};
        const response = await instance.get('/reports/numeric-profile', { params });
        return response.data; // { success, data }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const getTextPatterns = async (topN = 12) => {
    try {
        const response = await instance.get('/reports/text-patterns', { params: { top_n: topN } });
        return response.data; // { success, data }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const getDescriptions = async (clusterCol, topN = 12, zHigh = 0.7, zLow = -0.7) => {
    try {
        const response = await instance.get('/reports/descriptions', {
            params: {
                cluster_col: clusterCol,
                top_n: topN,
                z_high: zHigh,
                z_low: zLow,
            },
        });
        return response.data; // { success, data }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const exportReports = async (clusterCol, topN = 12, zHigh = 0.7, zLow = -0.7) => {
    try {
        const response = await instance.post('/reports/export', {
            cluster_col: clusterCol,
            top_n: topN,
            z_high: zHigh,
            z_low: zLow,
        });
        return response.data; // { success, data }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

// ------------------ Evaluación de Clustering ------------------
export const getClusteringEvaluation = async () => {
    try {
        const response = await instance.get('/evaluation/clustering');
        return response.data; // { success, evaluations, errors }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const evaluateKMeansModel = async () => {
    try {
        const response = await instance.get('/evaluation/clustering/kmeans');
        return response.data; // { success, evaluation }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const evaluateHierarchicalModel = async () => {
    try {
        const response = await instance.get('/evaluation/clustering/hierarchical');
        return response.data; // { success, evaluation }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const evaluateTextKMeansModel = async () => {
    try {
        const response = await instance.get('/evaluation/clustering/text');
        return response.data; // { success, evaluation }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const evaluateAutoKModel = async () => {
    try {
        const response = await instance.get('/evaluation/clustering/auto-k');
        return response.data; // { success, evaluation }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};
