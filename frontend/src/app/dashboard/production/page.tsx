'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { productionApi, hrApi } from '@/services/api';
import {
  Box, Container, Typography, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, IconButton, Card,
  CardContent, Grid, CircularProgress, Button, Select, MenuItem, FormControl, InputLabel
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

interface ProductionOrder {
  id: number;
  order_number: string;
  product_id: number;
  quantity_planned: number;
  quantity_completed: number;
  status: string;
  priority: string;
  scheduled_start?: string;
  scheduled_end?: string;
}

interface Product {
  id: number;
  sku: string;
  name: string;
}

export default function ProductionPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [orders, setOrders] = useState<ProductionOrder[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
      return;
    }
    loadData();
  }, [isAuthenticated, router]);

  const loadData = async () => {
    try {
      const [ordersRes, productsRes] = await Promise.all([
        productionApi.getOrders(),
        productionApi.getProducts(),
      ]);
      setOrders(ordersRes.data || []);
      setProducts(productsRes.data || []);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartOrder = async (id: number) => {
    try {
      await productionApi.startOrder(id);
      loadData();
    } catch (error) {
      console.error('Failed to start order:', error);
    }
  };

  const handleCompleteOrder = async (id: number, quantity: number) => {
    try {
      await productionApi.completeOrder(id, quantity);
      loadData();
    } catch (error) {
      console.error('Failed to complete order:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'default';
      case 'planned': return 'info';
      case 'released': return 'warning';
      case 'in_progress': return 'primary';
      case 'completed': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getProduct_name = (product_id: number) => {
    return products.find(p => p.id === product_id)?.name || `Product #${product_id}`;
  };

  const filteredOrders = statusFilter === 'all' 
    ? orders 
    : orders.filter(o => o.status === statusFilter);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Production Orders
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => router.push('/dashboard/kanban')}
        >
          View Kanban
        </Button>
      </Box>

      <Paper sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth size="small">
              <InputLabel>Status Filter</InputLabel>
              <Select
                value={statusFilter}
                label="Status Filter"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="all">All Statuses</MenuItem>
                <MenuItem value="draft">Draft</MenuItem>
                <MenuItem value="planned">Planned</MenuItem>
                <MenuItem value="released">Released</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="cancelled">Cancelled</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="textSecondary">
              Total: {filteredOrders.length} orders
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Order #</TableCell>
                <TableCell>Product</TableCell>
                <TableCell align="right">Qty Planned</TableCell>
                <TableCell align="right">Qty Completed</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Scheduled Start</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredOrders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell>{order.order_number}</TableCell>
                  <TableCell>{getProduct_name(order.product_id)}</TableCell>
                  <TableCell align="right">{order.quantity_planned}</TableCell>
                  <TableCell align="right">{order.quantity_completed}</TableCell>
                  <TableCell>
                    <Chip
                      label={order.status.replace('_', ' ')}
                      color={getStatusColor(order.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={order.priority}
                      color={order.priority === 'urgent' ? 'error' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {order.scheduled_start 
                      ? new Date(order.scheduled_start).toLocaleDateString()
                      : '-'
                    }
                  </TableCell>
                  <TableCell align="right">
                    {order.status === 'draft' || order.status === 'planned' ? (
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={() => handleStartOrder(order.id)}
                      >
                        <PlayArrowIcon />
                      </IconButton>
                    ) : order.status === 'in_progress' ? (
                      <IconButton 
                        size="small" 
                        color="success"
                        onClick={() => handleCompleteOrder(order.id, order.quantity_planned)}
                      >
                        <CheckCircleIcon />
                      </IconButton>
                    ) : null}
                    <IconButton size="small" onClick={() => {}}>
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {filteredOrders.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    No production orders found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
}
