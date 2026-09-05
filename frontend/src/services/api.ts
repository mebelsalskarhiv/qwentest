import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth-storage');
      if (token) {
        try {
          const parsed = JSON.parse(token);
          if (parsed.state?.accessToken) {
            config.headers.Authorization = `Bearer ${parsed.state.accessToken}`;
          }
        } catch (e) {
          // Ignore parsing errors
        }
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (username: string, password: string) =>
    apiClient.post('/auth/login', { username, password }),
  
  register: (data: any) =>
    apiClient.post('/auth/register', data),
  
  getMe: () =>
    apiClient.get('/auth/me'),
};

// Inventory API
export const inventoryApi = {
  getItems: (params?: any) =>
    apiClient.get('/inventory/items', { params }),
  
  getItem: (id: number) =>
    apiClient.get(`/inventory/items/${id}`),
  
  createItem: (data: any) =>
    apiClient.post('/inventory/items', data),
  
  updateItem: (id: number, data: any) =>
    apiClient.put(`/inventory/items/${id}`, data),
  
  createMovement: (itemId: number, data: any) =>
    apiClient.post(`/inventory/items/${itemId}/movements`, data),
  
  getCategories: () =>
    apiClient.get('/inventory/categories'),
  
  getSuppliers: () =>
    apiClient.get('/inventory/suppliers'),
};

// Production API
export const productionApi = {
  getOrders: (params?: any) =>
    apiClient.get('/production/orders', { params }),
  
  getOrder: (id: number) =>
    apiClient.get(`/production/orders/${id}`),
  
  createOrder: (data: any) =>
    apiClient.post('/production/orders', data),
  
  updateOrder: (id: number, data: any) =>
    apiClient.put(`/production/orders/${id}`, data),
  
  startOrder: (id: number) =>
    apiClient.post(`/production/orders/${id}/start`),
  
  completeOrder: (id: number, quantity: number) =>
    apiClient.post(`/production/orders/${id}/complete?quantity_completed=${quantity}`),
  
  getProducts: () =>
    apiClient.get('/production/products'),
  
  createProduct: (data: any) =>
    apiClient.post('/production/products', data),
  
  getWorkCenters: () =>
    apiClient.get('/production/work-centers'),
  
  createWorkCenter: (data: any) =>
    apiClient.post('/production/work-centers', data),
  
  getOperations: (orderId: number) =>
    apiClient.get(`/production/orders/${orderId}/operations`),
  
  createOperation: (orderId: number, data: any) =>
    apiClient.post(`/production/orders/${orderId}/operations`, data),
  
  getBOM: (productId: number) =>
    apiClient.get(`/production/products/${productId}/bom`),
  
  addBOM: (productId: number, data: any) =>
    apiClient.post(`/production/products/${productId}/bom`, data),
};

// HR & Stations API
export const hrApi = {
  // Employees
  getEmployees: (params?: any) =>
    apiClient.get('/hr/employees', { params }),
  
  getEmployee: (id: number) =>
    apiClient.get(`/hr/employees/${id}`),
  
  createEmployee: (data: any) =>
    apiClient.post('/hr/employees', data),
  
  updateEmployee: (id: number, data: any) =>
    apiClient.put(`/hr/employees/${id}`, data),
  
  deleteEmployee: (id: number) =>
    apiClient.delete(`/hr/employees/${id}`),
  
  // Departments
  getDepartments: () =>
    apiClient.get('/hr/departments'),
  
  createDepartment: (data: any) =>
    apiClient.post('/hr/departments', data),
  
  updateDepartment: (id: number, data: any) =>
    apiClient.put(`/hr/departments/${id}`, data),
  
  // Customers
  getCustomers: (params?: any) =>
    apiClient.get('/hr/customers', { params }),
  
  createCustomer: (data: any) =>
    apiClient.post('/hr/customers', data),
  
  updateCustomer: (id: number, data: any) =>
    apiClient.put(`/hr/customers/${id}`, data),
  
  // Stations
  getStations: (params?: any) =>
    apiClient.get('/hr/stations', { params }),
  
  getStation: (id: number) =>
    apiClient.get(`/hr/stations/${id}`),
  
  createStation: (data: any) =>
    apiClient.post('/hr/stations', data),
  
  updateStation: (id: number, data: any) =>
    apiClient.put(`/hr/stations/${id}`, data),
  
  updateStationStatus: (id: number, status: string) =>
    apiClient.post(`/hr/stations/${id}/status?status=${status}`),
};
