'use client';

import { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { inventoryApi, type InventoryItem } from '@/lib/api/inventory';

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null);
  const [formData, setFormData] = useState({
    sku: '',
    name: '',
    description: '',
    unit_of_measure: 'pcs',
    quantity_on_hand: 0,
    reorder_point: 10,
    unit_cost: 0,
  });

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      setLoading(true);
      const data = await inventoryApi.getItems();
      setItems(data);
      setError(null);
    } catch (err) {
      setError('Не удалось загрузить складские позиции');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (item?: InventoryItem) => {
    if (item) {
      setEditingItem(item);
      setFormData({
        sku: item.sku,
        name: item.name,
        description: item.description || '',
        unit_of_measure: item.unit_of_measure,
        quantity_on_hand: item.quantity_on_hand,
        reorder_point: item.reorder_point,
        unit_cost: Number(item.unit_cost),
      });
    } else {
      setEditingItem(null);
      setFormData({
        sku: '',
        name: '',
        description: '',
        unit_of_measure: 'pcs',
        quantity_on_hand: 0,
        reorder_point: 10,
        unit_cost: 0,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingItem(null);
  };

  const handleSubmit = async () => {
    try {
      if (editingItem) {
        await inventoryApi.updateItem(editingItem.id, formData);
      } else {
        await inventoryApi.createItem(formData);
      }
      handleCloseDialog();
      loadItems();
    } catch (err) {
      setError(editingItem ? 'Не удалось обновить позицию' : 'Не удалось создать позицию');
      console.error(err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить эту позицию?')) return;
    
    try {
      await inventoryApi.deleteItem(id);
      loadItems();
    } catch (err) {
      setError('Не удалось удалить позицию');
      console.error(err);
    }
  };

  if (loading) {
    return <Box sx={{ p: 3 }}><Typography>Загрузка...</Typography></Box>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Управление складом
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Добавить позицию
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>SKU</TableCell>
              <TableCell>Наименование</TableCell>
              <TableCell>Категория</TableCell>
              <TableCell>На складе</TableCell>
              <TableCell>Точка заказа</TableCell>
              <TableCell>Цена за единицу</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell align="right">Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.sku}</TableCell>
                <TableCell>{item.name}</TableCell>
                <TableCell>{item.category?.name || 'Нет данных'}</TableCell>
                <TableCell>{item.quantity_on_hand}</TableCell>
                <TableCell>{item.reorder_point}</TableCell>
                <TableCell>${Number(item.unit_cost).toFixed(2)}</TableCell>
                <TableCell>
                  <Chip
                    label={item.quantity_on_hand <= item.reorder_point ? 'Низкий остаток' : 'В наличии'}
                    color={item.quantity_on_hand <= item.reorder_point ? 'warning' : 'success'}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleOpenDialog(item)}>
                    <EditIcon />
                  </IconButton>
                  <IconButton size="small" onClick={() => handleDelete(item.id)} color="error">
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {items.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  Складские позиции не найдены
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingItem ? 'Редактирование позиции' : 'Новая складская позиция'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="SKU"
              value={formData.sku}
              onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Наименование"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Описание"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
            <TextField
              label="Единица измерения"
              value={formData.unit_of_measure}
              onChange={(e) => setFormData({ ...formData, unit_of_measure: e.target.value })}
              fullWidth
            />
            <TextField
              label="Количество на складе"
              type="number"
              value={formData.quantity_on_hand}
              onChange={(e) => setFormData({ ...formData, quantity_on_hand: parseInt(e.target.value) || 0 })}
              fullWidth
            />
            <TextField
              label="Точка заказа"
              type="number"
              value={formData.reorder_point}
              onChange={(e) => setFormData({ ...formData, reorder_point: parseInt(e.target.value) || 0 })}
              fullWidth
            />
            <TextField
              label="Цена за единицу"
              type="number"
              value={formData.unit_cost}
              onChange={(e) => setFormData({ ...formData, unit_cost: parseFloat(e.target.value) || 0 })}
              fullWidth
              inputProps={{ step: 0.01 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Отмена</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingItem ? 'Сохранить' : 'Создать'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
