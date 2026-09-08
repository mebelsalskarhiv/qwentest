/**
 * Equipment and OEE API client
 */

import { apiClient } from '@/services/api';
import type { Equipment, OEELog, MaintenanceRequest, EquipmentStatus } from '@/types/equipment';

export const equipmentApi = {
  // Equipment CRUD
  getAll: async (params?: { status?: EquipmentStatus; category?: string }) => {
    const response = await apiClient.get('/api/v1/equipment', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await apiClient.get(`/api/v1/equipment/${id}`);
    return response.data;
  },

  create: async (data: Partial<Equipment>) => {
    const response = await apiClient.post('/api/v1/equipment', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Equipment>) => {
    const response = await apiClient.put(`/api/v1/equipment/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await apiClient.delete(`/api/v1/equipment/${id}`);
    return response.data;
  },

  // OEE Logs
  getOEELogs: async (equipmentId: number, params?: { start_date?: string; end_date?: string }) => {
    const response = await apiClient.get(`/api/v1/equipment/${equipmentId}/oee`, { params });
    return response.data;
  },

  calculateOEE: async (equipmentId: number, data: { start_time: string; end_time: string }) => {
    const response = await apiClient.post(`/api/v1/equipment/${equipmentId}/oee/calculate`, data);
    return response.data;
  },

  // Maintenance Requests
  getMaintenanceRequests: async (equipmentId?: number, status?: string) => {
    const params: any = {};
    if (equipmentId) params.equipment_id = equipmentId;
    if (status) params.status = status;
    const response = await apiClient.get('/api/v1/maintenance/requests', { params });
    return response.data;
  },

  createMaintenanceRequest: async (data: Partial<MaintenanceRequest>) => {
    const response = await apiClient.post('/api/v1/maintenance/requests', data);
    return response.data;
  },

  updateMaintenanceRequest: async (id: number, data: Partial<MaintenanceRequest>) => {
    const response = await apiClient.put(`/api/v1/maintenance/requests/${id}`, data);
    return response.data;
  },

  // Sensor Data (Real-time)
  getSensorData: async (equipmentId: number, params?: { hours?: number }) => {
    const response = await apiClient.get(`/api/v1/equipment/${equipmentId}/sensors`, { params });
    return response.data;
  },

  // Downtime Events
  getDowntimeEvents: async (equipmentId: number, params?: { start_date?: string; end_date?: string }) => {
    const response = await apiClient.get(`/api/v1/equipment/${equipmentId}/downtime`, { params });
    return response.data;
  },

  reportDowntime: async (equipmentId: number, data: { reason_code: string; description: string }) => {
    const response = await apiClient.post(`/api/v1/equipment/${equipmentId}/downtime`, data);
    return response.data;
  },
};

export default equipmentApi;
