'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { productionApi } from '@/services/api';
import {
  Box, Container, Typography, Paper, Card, CardContent, Grid,
  CircularProgress, Chip, IconButton, Tooltip
} from '@mui/material';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import EditIcon from '@mui/icons-material/Edit';

interface ProductionOrder {
  id: number;
  order_number: string;
  product_id: number;
  quantity_planned: number;
  quantity_completed: number;
  status: string;
  priority: string;
}

const COLUMNS = [
  { id: 'draft', title: 'Draft', color: '#9e9e9e' },
  { id: 'planned', title: 'Planned', color: '#2196f3' },
  { id: 'released', title: 'Released', color: '#ff9800' },
  { id: 'in_progress', title: 'In Progress', color: '#9c27b0' },
  { id: 'completed', title: 'Completed', color: '#4caf50' },
];

export default function KanbanPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [orders, setOrders] = useState<Record<string, ProductionOrder[]>>({});
  const [loading, setLoading] = useState(true);
  const [draggedOrder, setDraggedOrder] = useState<ProductionOrder | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
      return;
    }
    loadData();
  }, [isAuthenticated, router]);

  const loadData = async () => {
    try {
      const res = await productionApi.getOrders();
      const ordersList = res.data || [];
      
      // Group by status
      const grouped: Record<string, ProductionOrder[]> = {};
      COLUMNS.forEach(col => {
        grouped[col.id] = ordersList.filter((o: ProductionOrder) => o.status === col.id);
      });
      
      setOrders(grouped);
    } catch (error) {
      console.error('Failed to load orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDragStart = (order: ProductionOrder) => {
    setDraggedOrder(order);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = async (status: string) => {
    if (!draggedOrder || draggedOrder.status === status) {
      setDraggedOrder(null);
      return;
    }

    try {
      // Update order status via API
      const updateData = { status };
      await productionApi.updateOrder(draggedOrder.id, updateData);
      loadData();
    } catch (error) {
      console.error('Failed to update order status:', error);
    } finally {
      setDraggedOrder(null);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Production Kanban
      </Typography>
      <Typography variant="body2" color="textSecondary" paragraph>
        Drag and drop cards between columns to change order status
      </Typography>

      <Grid container spacing={2} sx={{ height: 'calc(100vh - 200px)' }}>
        {COLUMNS.map((column) => (
          <Grid item xs={12} sm={6} md={2.4} key={column.id}>
            <Paper
              sx={{
                height: '100%',
                bgcolor: '#f5f5f5',
                display: 'flex',
                flexDirection: 'column',
              }}
              onDragOver={handleDragOver}
              onDrop={() => handleDrop(column.id)}
            >
              <Box
                sx={{
                  p: 2,
                  bgcolor: column.color,
                  color: 'white',
                  fontWeight: 'bold',
                }}
              >
                {column.title} ({orders[column.id]?.length || 0})
              </Box>
              <Box sx={{ p: 2, flex: 1, overflow: 'auto' }}>
                {(orders[column.id] || []).map((order) => (
                  <Card
                    key={order.id}
                    draggable
                    onDragStart={() => handleDragStart(order)}
                    sx={{
                      mb: 2,
                      cursor: 'grab',
                      '&:active': { cursor: 'grabbing' },
                      borderLeft: `4px solid ${column.color}`,
                    }}
                  >
                    <CardContent sx={{ p: 2 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {order.order_number}
                        </Typography>
                        <Tooltip title="Drag to move">
                          <DragIndicatorIcon fontSize="small" color="action" />
                        </Tooltip>
                      </Box>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Qty: {order.quantity_completed}/{order.quantity_planned}
                      </Typography>
                      <Chip
                        label={order.priority}
                        color={getPriorityColor(order.priority) as any}
                        size="small"
                      />
                      <Box mt={1}>
                        <IconButton size="small" onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/dashboard/production`);
                        }}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}
