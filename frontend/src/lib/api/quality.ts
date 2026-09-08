/**
 * Quality Control API client
 */

import { apiClient } from '@/services/api';
import type { 
  DefectType, 
  QualityCheck, 
  QualityDefect, 
  CorrectiveAction, 
  SPCChart, 
  SPCDataPoint,
  QualityStats 
} from '@/types/quality';

export const qualityApi = {
  // Defect Types
  getDefectTypes: async (params?: { category?: string; is_active?: boolean }) => {
    const response = await apiClient.get('/api/v1/quality/defect-types', { params });
    return response.data;
  },

  getDefectType: async (id: number) => {
    const response = await apiClient.get(`/api/v1/quality/defect-types/${id}`);
    return response.data;
  },

  createDefectType: async (data: Partial<DefectType>) => {
    const response = await apiClient.post('/api/v1/quality/defect-types', data);
    return response.data;
  },

  updateDefectType: async (id: number, data: Partial<DefectType>) => {
    const response = await apiClient.put(`/api/v1/quality/defect-types/${id}`, data);
    return response.data;
  },

  deleteDefectType: async (id: number) => {
    const response = await apiClient.delete(`/api/v1/quality/defect-types/${id}`);
    return response.data;
  },

  // Quality Checks
  getQualityChecks: async (params?: { 
    stage_id?: number; 
    work_order_id?: number; 
    status?: string;
    check_type?: string;
  }) => {
    const response = await apiClient.get('/api/v1/quality/checks', { params });
    return response.data;
  },

  getQualityCheck: async (id: number) => {
    const response = await apiClient.get(`/api/v1/quality/checks/${id}`);
    return response.data;
  },

  createQualityCheck: async (data: Partial<QualityCheck>) => {
    const response = await apiClient.post('/api/v1/quality/checks', data);
    return response.data;
  },

  updateQualityCheck: async (id: number, data: Partial<QualityCheck>) => {
    const response = await apiClient.put(`/api/v1/quality/checks/${id}`, data);
    return response.data;
  },

  addDefect: async (checkId: number, defectData: Partial<QualityDefect>) => {
    const response = await apiClient.post(`/api/v1/quality/checks/${checkId}/defects`, defectData);
    return response.data;
  },

  completeCheck: async (id: number, data: { passed_quantity: number; rejected_quantity: number; notes?: string }) => {
    const response = await apiClient.post(`/api/v1/quality/checks/${id}/complete`, data);
    return response.data;
  },

  // Corrective Actions
  getCorrectiveActions: async (params?: { status?: string; assigned_to?: number; priority?: string }) => {
    const response = await apiClient.get('/api/v1/quality/corrective-actions', { params });
    return response.data;
  },

  getCorrectiveAction: async (id: number) => {
    const response = await apiClient.get(`/api/v1/quality/corrective-actions/${id}`);
    return response.data;
  },

  createCorrectiveAction: async (data: Partial<CorrectiveAction>) => {
    const response = await apiClient.post('/api/v1/quality/corrective-actions', data);
    return response.data;
  },

  updateCorrectiveAction: async (id: number, data: Partial<CorrectiveAction>) => {
    const response = await apiClient.put(`/api/v1/quality/corrective-actions/${id}`, data);
    return response.data;
  },

  approveAction: async (id: number) => {
    const response = await apiClient.post(`/api/v1/quality/corrective-actions/${id}/approve`);
    return response.data;
  },

  completeAction: async (id: number, data: { lessons_learned?: string }) => {
    const response = await apiClient.post(`/api/v1/quality/corrective-actions/${id}/complete`, data);
    return response.data;
  },

  // SPC Charts
  getSPCCharts: async (params?: { product_id?: number; is_active?: boolean }) => {
    const response = await apiClient.get('/api/v1/quality/spc-charts', { params });
    return response.data;
  },

  getSPCChart: async (id: number) => {
    const response = await apiClient.get(`/api/v1/quality/spc-charts/${id}`);
    return response.data;
  },

  createSPCChart: async (data: Partial<SPCChart>) => {
    const response = await apiClient.post('/api/v1/quality/spc-charts', data);
    return response.data;
  },

  updateSPCChart: async (id: number, data: Partial<SPCChart>) => {
    const response = await apiClient.put(`/api/v1/quality/spc-charts/${id}`, data);
    return response.data;
  },

  addDataPoint: async (chartId: number, data: Partial<SPCDataPoint>) => {
    const response = await apiClient.post(`/api/v1/quality/spc-charts/${chartId}/data-points`, data);
    return response.data;
  },

  getChartData: async (chartId: number, params?: { limit?: number }) => {
    const response = await apiClient.get(`/api/v1/quality/spc-charts/${chartId}/data`, { params });
    return response.data;
  },

  // Statistics
  getQualityStats: async (params?: { start_date?: string; end_date?: string; product_id?: number }) => {
    const response = await apiClient.get('/api/v1/quality/statistics', { params });
    return response.data as QualityStats;
  },
};

export default qualityApi;
