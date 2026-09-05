import { apiClient } from '@/services/api';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  role_ids?: number[];
  roles?: Role[];
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role_ids?: number[];
  is_active?: boolean;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  password?: string;
  role_ids?: number[];
  is_active?: boolean;
}

export const userApi = {
  getUsers: async (): Promise<User[]> => {
    const response = await apiClient.get('/users');
    return response.data;
  },

  getUser: async (id: number): Promise<User> => {
    const response = await apiClient.get(`/users/${id}`);
    return response.data;
  },

  createUser: async (data: UserCreate): Promise<User> => {
    const response = await apiClient.post('/users', data);
    return response.data;
  },

  updateUser: async (id: number, data: UserUpdate): Promise<User> => {
    const response = await apiClient.put(`/users/${id}`, data);
    return response.data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await apiClient.delete(`/users/${id}`);
  },
};
