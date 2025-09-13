import axios from 'axios';

// Configuración base para la API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Cliente axios configurado
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Interceptor para manejo de errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Tipos para los buses (basados en tu API)
export interface Bus {
  id: number;
  patente: string;
  marca: string;
  modelo: string;
  año: number;
  estado: string;
  combustible: string;
  capacidad: number;
  kilometraje?: number;
  precio?: number;
  observaciones?: string;
  codigo_interno?: string;
  numero_chasis?: string;
  numero_motor?: string;
  fecha_compra?: string;
}

export interface BusCreate {
  patente: string;
  marca: string;
  modelo: string;
  año: number;
  capacidad_sentados: number;
  estado_id: number;
  tipo_combustible_id: number;
  codigo_interno?: string;
  numero_chasis?: string;
  numero_motor?: string;
  kilometraje_actual?: number;
  fecha_compra?: string;
  precio_compra?: number;
  observaciones?: string;
}

export interface Estado {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string;
}

export interface TipoCombustible {
  id: number;
  codigo: string;
  nombre: string;
  factor_emision?: number;
}

// Funciones de la API
export const busesApi = {
  // Listar buses
  getBuses: async () => {
    const response = await apiClient.get('/api/v1/buses/');
    return response.data;
  },

  // Obtener bus por ID
  getBus: async (id: number) => {
    const response = await apiClient.get(`/api/v1/buses/${id}`);
    return response.data;
  },

  // Crear bus
  createBus: async (bus: BusCreate) => {
    const response = await apiClient.post('/api/v1/buses/', bus);
    return response.data;
  },

  // Actualizar bus
  updateBus: async (id: number, bus: Partial<BusCreate>) => {
    const response = await apiClient.put(`/api/v1/buses/${id}`, bus);
    return response.data;
  },

  // Eliminar bus
  deleteBus: async (id: number) => {
    const response = await apiClient.delete(`/api/v1/buses/${id}`);
    return response.data;
  },

  // Obtener estados disponibles
  getEstados: async (): Promise<{ estados: Estado[] }> => {
    const response = await apiClient.get('/api/v1/buses/auxiliares/estados');
    return response.data;
  },

  // Obtener tipos de combustible
  getTiposCombustible: async (): Promise<{ tipos_combustible: TipoCombustible[] }> => {
    const response = await apiClient.get('/api/v1/buses/auxiliares/combustibles');
    return response.data;
  },

  // Obtener estadísticas
  getEstadisticas: async () => {
    const response = await apiClient.get('/api/v1/buses/reportes/estadisticas');
    return response.data;
  }
};

// Funciones del sistema
export const systemApi = {
  // Health check
  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Información del sistema
  getInfo: async () => {
    const response = await apiClient.get('/info');
    return response.data;
  }
};