'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { productionApi, inventoryApi } from '@/services/api';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  CssBaseline,
  Container,
  Grid,
  Paper,
  Card,
  CardContent,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import InventoryIcon from '@mui/icons-material/Inventory';
import FactoryIcon from '@mui/icons-material/Factory';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import AssessmentIcon from '@mui/icons-material/Assessment';

const drawerWidth = 240;

interface DashboardStats {
  productionOrders: number;
  inventoryItems: number;
  activeOrders: number;
  lowStockItems: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, logout, user } = useAuthStore();
  const [mobileOpen, setMobileOpen] = useState(false);
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

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Production', icon: <FactoryIcon />, path: '/dashboard/production' },
    { text: 'Kanban', icon: <FactoryIcon />, path: '/dashboard/kanban' },
    { text: 'Inventory', icon: <InventoryIcon />, path: '/dashboard/inventory' },
    { text: 'Employees', icon: <SettingsIcon />, path: '/dashboard/employees' },
    { text: 'Departments', icon: <SettingsIcon />, path: '/dashboard/departments' },
    { text: 'Customers', icon: <SettingsIcon />, path: '/dashboard/customers' },
    { text: 'Stations', icon: <SettingsIcon />, path: '/dashboard/stations' },
    { text: 'Users', icon: <SettingsIcon />, path: '/dashboard/users' },
    { text: 'Roles', icon: <SettingsIcon />, path: '/dashboard/roles' },
    { text: 'Reports', icon: <AssessmentIcon />, path: '/dashboard/reports' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/dashboard/settings' },
  ];

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap>
          Virtuoso MES
        </Typography>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton onClick={() => router.push(item.path)}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout}>
            <ListItemIcon>
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText primary="Logout" />
          </ListItemButton>
        </ListItem>
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setMobileOpen(!mobileOpen)}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Dashboard
          </Typography>
          <Typography variant="body2">
            {user?.username} ({user?.role})
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="h4" gutterBottom>
            Production Overview
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Orders
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
                    Active Orders
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
                    Inventory Items
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
                    Low Stock Alerts
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
              Welcome to Virtuoso MES
            </Typography>
            <Typography variant="body1" color="textSecondary">
              This is your manufacturing execution system dashboard. Use the navigation menu to access different modules:
            </Typography>
            <List>
              <ListItem>
                <ListItemText primary="Production - Manage production orders, work centers, and operations" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Inventory - Track inventory items, stock movements, and suppliers" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Reports - View analytics and generate reports" />
              </ListItem>
            </List>
          </Paper>
        </Container>
      </Box>
    </Box>
  );
}
