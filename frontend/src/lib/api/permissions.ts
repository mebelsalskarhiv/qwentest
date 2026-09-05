import { apiClient } from '@/services/api';

export interface Permission {
  id: number;
  name: string;
  description?: string;
  resource: string;
  action: string;
  created_at: string;
}

export const permissionApi = {
  getPermissions: async (): Promise<Permission[]> => {
    const response = await apiClient.get('/permissions');
    return response.data;
  },

  getPermission: async (id: number): Promise<Permission> => {
    const response = await apiClient.get(`/permissions/${id}`);
    return response.data;
  },
};
