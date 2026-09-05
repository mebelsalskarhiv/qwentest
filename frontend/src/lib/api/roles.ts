import { apiClient } from '@/services/api';

export interface Role {
  id: number;
  name: string;
  description?: string;
  permissions?: Permission[];
  users?: any[];
  created_at: string;
  updated_at: string;
}

export interface RoleCreate {
  name: string;
  description?: string;
  permission_ids?: number[];
}

export interface RoleUpdate {
  name?: string;
  description?: string;
  permission_ids?: number[];
}

export const roleApi = {
  getRoles: async (): Promise<Role[]> => {
    const response = await apiClient.get('/roles');
    return response.data;
  },

  getRole: async (id: number): Promise<Role> => {
    const response = await apiClient.get(`/roles/${id}`);
    return response.data;
  },

  createRole: async (data: RoleCreate): Promise<Role> => {
    const response = await apiClient.post('/roles', data);
    return response.data;
  },

  updateRole: async (id: number, data: RoleUpdate): Promise<Role> => {
    const response = await apiClient.put(`/roles/${id}`, data);
    return response.data;
  },

  deleteRole: async (id: number): Promise<void> => {
    await apiClient.delete(`/roles/${id}`);
  },
};
