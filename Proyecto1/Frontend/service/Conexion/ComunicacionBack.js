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
        return response.data; // { message, metadata }
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

// Aquí se pueden agregar más funciones de comunicación con el backend
// export const otraFuncion = async (data) => { ... }
