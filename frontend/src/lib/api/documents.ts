/**
 * Documents API client
 */

import { apiClient } from '@/services/api';
import type { 
  Document, 
  DocumentCategory, 
  DocumentVersion, 
  DocumentLink,
  DocumentStats 
} from '@/types/documents';

export const documentsApi = {
  // Categories
  getCategories: async (params?: { category_type?: string; is_active?: boolean }) => {
    const response = await apiClient.get('/api/v1/documents/categories', { params });
    return response.data;
  },

  getCategory: async (id: number) => {
    const response = await apiClient.get(`/api/v1/documents/categories/${id}`);
    return response.data;
  },

  createCategory: async (data: Partial<DocumentCategory>) => {
    const response = await apiClient.post('/api/v1/documents/categories', data);
    return response.data;
  },

  updateCategory: async (id: number, data: Partial<DocumentCategory>) => {
    const response = await apiClient.put(`/api/v1/documents/categories/${id}`, data);
    return response.data;
  },

  deleteCategory: async (id: number) => {
    const response = await apiClient.delete(`/api/v1/documents/categories/${id}`);
    return response.data;
  },

  // Documents
  getDocuments: async (params?: { 
    category_id?: number; 
    status?: string; 
    owner_id?: number;
    is_mandatory?: boolean;
  }) => {
    const response = await apiClient.get('/api/v1/documents', { params });
    return response.data;
  },

  getDocument: async (id: number) => {
    const response = await apiClient.get(`/api/v1/documents/${id}`);
    return response.data;
  },

  createDocument: async (data: Partial<Document>) => {
    const response = await apiClient.post('/api/v1/documents', data);
    return response.data;
  },

  updateDocument: async (id: number, data: Partial<Document>) => {
    const response = await apiClient.put(`/api/v1/documents/${id}`, data);
    return response.data;
  },

  deleteDocument: async (id: number) => {
    const response = await apiClient.delete(`/api/v1/documents/${id}`);
    return response.data;
  },

  // Document Versions
  uploadVersion: async (documentId: number, formData: FormData) => {
    const response = await apiClient.post(
      `/api/v1/documents/${documentId}/versions`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  getVersions: async (documentId: number) => {
    const response = await apiClient.get(`/api/v1/documents/${documentId}/versions`);
    return response.data;
  },

  downloadVersion: async (documentId: number, versionId: number) => {
    const response = await apiClient.get(
      `/api/v1/documents/${documentId}/versions/${versionId}/download`,
      { responseType: 'blob' }
    );
    return response.data;
  },

  approveVersion: async (documentId: number, versionId: number) => {
    const response = await apiClient.post(
      `/api/v1/documents/${documentId}/versions/${versionId}/approve`
    );
    return response.data;
  },

  // Document Links
  getLinkedObjects: async (documentId: number) => {
    const response = await apiClient.get(`/api/v1/documents/${documentId}/links`);
    return response.data;
  },

  addLink: async (documentId: number, linkData: Partial<DocumentLink>) => {
    const response = await apiClient.post(`/api/v1/documents/${documentId}/links`, linkData);
    return response.data;
  },

  removeLink: async (documentId: number, linkId: number) => {
    const response = await apiClient.delete(`/api/v1/documents/${documentId}/links/${linkId}`);
    return response.data;
  },

  // Document Lifecycle
  submitForApproval: async (id: number) => {
    const response = await apiClient.post(`/api/v1/documents/${id}/submit-approval`);
    return response.data;
  },

  approveDocument: async (id: number) => {
    const response = await apiClient.post(`/api/v1/documents/${id}/approve`);
    return response.data;
  },

  obsoleteDocument: async (id: number, reason?: string) => {
    const response = await apiClient.post(`/api/v1/documents/${id}/obsolete`, { reason });
    return response.data;
  },

  // Statistics
  getDocumentStats: async (params?: { period?: string }) => {
    const response = await apiClient.get('/api/v1/documents/statistics', { params });
    return response.data as DocumentStats;
  },
};

export default documentsApi;
