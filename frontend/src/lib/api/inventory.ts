import { apiClient } from '@/services/api';

export interface InventoryItem {
  id: number;
  sku: string;
  name: string;
  description?: string;
  category_id?: number;
  category?: { id: number; name: string };
  unit_of_measure: string;
  quantity_on_hand: number;
  reorder_point: number;
  unit_cost: number;
  created_at: string;
  updated_at: string;
}

export interface InventoryCategory {
  id: number;
  name: string;
  description?: string;
}

export interface StockMovement {
  id: number;
  item_id: number;
  movement_type: 'in' | 'out' | 'adjustment';
  quantity: number;
  reference?: string;
  notes?: string;
  created_at: string;
}

export const inventoryApi = {
  getItems: async (params?: any): Promise<InventoryItem[]> => {
    const response = await apiClient.get('/inventory/items', { params });
    return response.data;
  },

  getItem: async (id: number): Promise<InventoryItem> => {
    const response = await apiClient.get(`/inventory/items/${id}`);
    return response.data;
  },

  createItem: async (data: Partial<InventoryItem>): Promise<InventoryItem> => {
    const response = await apiClient.post('/inventory/items', data);
    return response.data;
  },

  updateItem: async (id: number, data: Partial<InventoryItem>): Promise<InventoryItem> => {
    const response = await apiClient.put(`/inventory/items/${id}`, data);
    return response.data;
  },

  deleteItem: async (id: number): Promise<void> => {
    await apiClient.delete(`/inventory/items/${id}`);
  },

  getCategories: async (): Promise<InventoryCategory[]> => {
    const response = await apiClient.get('/inventory/categories');
    return response.data;
  },

  createMovement: async (itemId: number, data: Partial<StockMovement>): Promise<StockMovement> => {
    const response = await apiClient.post(`/inventory/items/${itemId}/movements`, data);
    return response.data;
  },
};
