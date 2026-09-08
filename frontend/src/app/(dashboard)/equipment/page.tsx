'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { equipmentApi } from '@/lib/api/equipment';
import type { Equipment, OEELog, MaintenanceRequest, EquipmentStatus } from '@/types/equipment';
import { useAuthStore } from '@/store/authStore';

const statusColors: Record<EquipmentStatus, 'default' | 'success' | 'warning' | 'error' | 'info'> = {
  offline: 'default',
  idle: 'info',
  running: 'success',
  setup: 'warning',
  paused: 'warning',
  down: 'error',
  maintenance: 'error',
};

export default function EquipmentDashboard() {
  const { user } = useAuthStore();
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [oeeData, setOEEData] = useState<OEELog[]>([]);
  const [maintenanceRequests, setMaintenanceRequests] = useState<MaintenanceRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'view' | 'edit' | 'create'>('view');

  const loadData = async () => {
    try {
      setLoading(true);
      const [eqData, maintData] = await Promise.all([
        equipmentApi.getAll(),
        equipmentApi.getMaintenanceRequests(),
      ]);
      setEquipment(eqData);
      setMaintenanceRequests(maintData);
      
      // Load OEE data for first equipment if available
      if (eqData.length > 0) {
        const oeeLogs = await equipmentApi.getOEELogs(eqData[0].id);
        setOEEData(oeeLogs);
      }
    } catch (error) {
      console.error('Failed to load equipment data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpenDialog = (mode: 'view' | 'edit' | 'create', eq?: Equipment) => {
    setDialogMode(mode);
    setSelectedEquipment(eq || null);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedEquipment(null);
  };

  const calculateAverageOEE = () => {
    if (oeeData.length === 0) return 0;
    const sum = oeeData.reduce((acc, log) => acc + log.oee_score, 0);
    return (sum / oeeData.length) * 100;
  };

  const getStatusCount = (status: EquipmentStatus) => {
    return equipment.filter(eq => eq.status === status).length;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const avgOEE = calculateAverageOEE();

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Оборудование и OEE
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog('create')}
        >
          Добавить оборудование
        </Button>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Всего оборудования
                  </Typography>
                  <Typography variant="h4">{equipment.length}</Typography>
                </Box>
                <TrendingUpIcon color="primary" sx={{ fontSize: 48, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Средний OEE
                  </Typography>
                  <Typography variant="h4" color={avgOEE >= 85 ? 'success.main' : avgOEE >= 70 ? 'warning.main' : 'error.main'}>
                    {avgOEE.toFixed(1)}%
                  </Typography>
                </Box>
                <TrendingUpIcon color="success" sx={{ fontSize: 48, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    В работе
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {getStatusCount('running')}
                  </Typography>
                </Box>
                <CheckCircleIcon color="success" sx={{ fontSize: 48, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Проблемы
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {getStatusCount('down') + getStatusCount('maintenance')}
                  </Typography>
                </Box>
                <WarningIcon color="error" sx={{ fontSize: 48, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* OEE Chart */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" mb={2}>
            Динамика OEE
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={oeeData.slice(-10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="start_time" tickFormatter={(val) => new Date(val).toLocaleDateString()} />
              <YAxis domain={[0, 100]} />
              <Tooltip labelFormatter={(val) => new Date(val).toLocaleString()} />
              <Legend />
              <Line type="monotone" dataKey="oee_score" name="OEE" stroke="#1976d2" strokeWidth={2} />
              <Line type="monotone" dataKey="availability" name="Доступность" stroke="#4caf50" />
              <Line type="monotone" dataKey="performance" name="Производительность" stroke="#ff9800" />
              <Line type="monotone" dataKey="quality" name="Качество" stroke="#f44336" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Equipment Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Оборудование</Typography>
            <IconButton onClick={loadData}>
              <RefreshIcon />
            </IconButton>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Код</TableCell>
                  <TableCell>Наименование</TableCell>
                  <TableCell>Категория</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>OEE</TableCell>
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {equipment.map((eq) => (
                  <TableRow key={eq.id}>
                    <TableCell>{eq.code}</TableCell>
                    <TableCell>{eq.name}</TableCell>
                    <TableCell>{eq.category || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={eq.status}
                        color={statusColors[eq.status]}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {eq.availability_target ? `${eq.availability_target}%` : '-'}
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => handleOpenDialog('view', eq)}>
                        <EditIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Equipment Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'create' ? 'Добавить оборудование' : 
           dialogMode === 'edit' ? 'Редактировать оборудование' : 'Просмотр оборудования'}
        </DialogTitle>
        <DialogContent>
          {selectedEquipment && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Код"
                  value={selectedEquipment.code}
                  fullWidth
                  disabled
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Наименование"
                  value={selectedEquipment.name}
                  fullWidth
                  disabled
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Категория"
                  value={selectedEquipment.category || ''}
                  fullWidth
                  disabled
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Статус"
                  value={selectedEquipment.status}
                  fullWidth
                  disabled
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Описание"
                  value={selectedEquipment.description || ''}
                  fullWidth
                  multiline
                  rows={3}
                  disabled
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Закрыть</Button>
          {dialogMode !== 'view' && (
            <Button variant="contained" onClick={handleCloseDialog}>
              Сохранить
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}
