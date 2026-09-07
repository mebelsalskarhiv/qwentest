'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { productionApi, inventoryApi } from '@/services/api';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Container,
  Grid,
  Paper,
  Card,
  CardContent,
} from '@mui/material';

interface DashboardStats {
  productionOrders: number;
  inventoryItems: number;
  activeOrders: number;
  lowStockItems: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats>({
    productionOrders: 0,
    inventoryItems: 0,
    activeOrders: 0,
    lowStockItems: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
      return;
    }

    // Load dashboard stats
    loadStats();
  }, [isAuthenticated, router]);

  const loadStats = async () => {
    try {
      const [ordersRes, itemsRes] = await Promise.all([
        productionApi.getOrders(),
        inventoryApi.getItems(),
      ]);
      
      const orders = ordersRes.data || [];
      const items = itemsRes.data || [];
      
      setStats({
        productionOrders: orders.length,
        inventoryItems: items.length,
        activeOrders: orders.filter((o: any) => 
          ['in_progress', 'released'].includes(o.status)
        ).length,
        lowStockItems: items.filter((i: any) => 
          i.current_stock <= i.min_stock_level
        ).length,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
          <Typography variant="h4" gutterBottom>
            Обзор производства
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Всего заказов
                  </Typography>
                  <Typography variant="h3">
                    {loading ? '-' : stats.productionOrders}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Активные заказы
                  </Typography>
                  <Typography variant="h3" color="primary">
                    {loading ? '-' : stats.activeOrders}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Позиции на складе
                  </Typography>
                  <Typography variant="h3">
                    {loading ? '-' : stats.inventoryItems}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Низкий остаток
                  </Typography>
                  <Typography variant="h3" color="error">
                    {loading ? '-' : stats.lowStockItems}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Paper sx={{ mt: 4, p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Добро пожаловать в Virtuoso MES
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Это панель управления производством. Используйте меню для перехода к нужному разделу:
            </Typography>
            <List>
              <ListItem>
                <ListItemText primary="Производство: заказы, рабочие центры и операции" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Склад: материалы, движения и поставщики" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Отчёты: аналитика и отчётность" />
              </ListItem>
            </List>
          </Paper>
    </Container>
  );
}
