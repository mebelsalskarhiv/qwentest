'use client';

import { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  LinearProgress,
} from '@mui/material';
import BuildIcon from '@mui/icons-material/Build';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { BarChart } from '@mui/x-charts/BarChart';
import { Gauge } from '@mui/x-charts/Gauge';
import equipmentApi from '@/lib/api/equipment';
import type { Equipment, OEELog, MaintenanceRequest } from '@/types/equipment';

export default function EquipmentPage() {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [oeeData, setOeeData] = useState<OEELog[]>([]);
  const [maintenanceRequests, setMaintenanceRequests] = useState<MaintenanceRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [equipData, oeeRes, maintData] = await Promise.all([
        equipmentApi.getAll(),
        equipmentApi.getOEELogs(1, { start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] }),
        equipmentApi.getMaintenanceRequests(undefined, 'in_progress'),
      ]);
      setEquipment(equipData);
      setOeeData(Array.isArray(oeeRes) ? oeeRes.slice(0, 10) : []);
      setMaintenanceRequests(maintData.slice(0, 5));
    } catch (error) {
      console.error('Failed to load equipment data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'success';
      case 'idle': return 'info';
      case 'setup': return 'warning';
      case 'down': return 'error';
      case 'maintenance': return 'default';
      default: return 'default';
    }
  };

  // Calculate average OEE
  const avgOEE = oeeData.length > 0 
    ? oeeData.reduce((sum, log) => sum + log.oee_score, 0) / oeeData.length 
    : 0;

  const avgAvailability = oeeData.length > 0 
    ? oeeData.reduce((sum, log) => sum + log.availability, 0) / oeeData.length 
    : 0;

  const avgPerformance = oeeData.length > 0 
    ? oeeData.reduce((sum, log) => sum + log.performance, 0) / oeeData.length 
    : 0;

  const avgQuality = oeeData.length > 0 
    ? oeeData.reduce((sum, log) => sum + log.quality, 0) / oeeData.length 
    : 0;

  if (loading) {
    return <Box sx={{ p: 3 }}><Typography>Loading...</Typography></Box>;
  }

  const runningCount = equipment.filter(e => e.status === 'running').length;
  const downCount = equipment.filter(e => e.status === 'down').length;
  const maintenanceCount = equipment.filter(e => e.status === 'maintenance').length;

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Оборудование и OEE
        </Typography>
        <Button variant="contained" startIcon={<BuildIcon />} onClick={() => {}}>
          Добавить оборудование
        </Button>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Средний OEE</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                <Gauge
                  value={avgOEE}
                  valueMax={100}
                />
              </Box>
              <Typography color="text.secondary" align="center">За неделю: {avgOEE.toFixed(1)}%</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <BuildIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Статус оборудования</Typography>
              </Box>
              <Typography variant="h3">{equipment.length}</Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">В работе</Typography>
                  <Typography variant="body2">{runningCount}</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={(runningCount / equipment.length) * 100} 
                  color="success"
                  sx={{ mb: 1 }}
                />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Простой</Typography>
                  <Typography variant="body2">{downCount}</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={(downCount / equipment.length) * 100} 
                  color="error"
                  sx={{ mb: 1 }}
                />
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">На ТО</Typography>
                  <Typography variant="body2">{maintenanceCount}</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={(maintenanceCount / equipment.length) * 100} 
                  color="warning"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircleIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Доступность</Typography>
              </Box>
              <Typography variant="h3">{avgAvailability.toFixed(1)}%</Typography>
              <Typography color="text.secondary">Средняя за неделю</Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">Производительность: {avgPerformance.toFixed(1)}%</Typography>
                <Typography variant="body2" color="text.secondary">Качество: {avgQuality.toFixed(1)}%</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <WarningIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Заявки на ТО</Typography>
              </Box>
              <Typography variant="h3">{maintenanceRequests.length}</Typography>
              <Typography color="text.secondary">Активных заявок</Typography>
              <Box sx={{ mt: 2 }}>
                {maintenanceRequests.slice(0, 3).map(req => (
                  <Typography key={req.id} variant="body2" sx={{ mb: 0.5 }}>
                    • {req.title}
                  </Typography>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* OEE Chart */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>OEE по дням</Typography>
          <Box sx={{ height: 300 }}>
            {oeeData.length > 0 && (
              <BarChart
                xAxis={[{ 
                  scaleType: 'band', 
                  data: oeeData.map(log => new Date(log.start_time).toLocaleDateString()) 
                }]}
                series={[
                  { 
                    data: oeeData.map(log => log.oee_score), 
                    label: 'OEE',
                    color: '#1976d2'
                  },
                  { 
                    data: oeeData.map(log => log.availability), 
                    label: 'Доступность',
                    color: '#4caf50'
                  },
                  { 
                    data: oeeData.map(log => log.performance), 
                    label: 'Производительность',
                    color: '#ff9800'
                  },
                  { 
                    data: oeeData.map(log => log.quality), 
                    label: 'Качество',
                    color: '#9c27b0'
                  },
                ]}
                width={800}
                height={300}
              />
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Equipment Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Оборудование</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Код</TableCell>
                  <TableCell>Название</TableCell>
                  <TableCell>Категория</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Расположение</TableCell>
                  <TableCell>OEE Цель</TableCell>
                  <TableCell>Следующее ТО</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {equipment.slice(0, 10).map((eq) => (
                  <TableRow key={eq.id}>
                    <TableCell>{eq.code}</TableCell>
                    <TableCell>{eq.name}</TableCell>
                    <TableCell>{eq.category || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={eq.status}
                        size="small"
                        color={getStatusColor(eq.status) as any}
                      />
                    </TableCell>
                    <TableCell>{eq.location || '-'}</TableCell>
                    <TableCell>{eq.availability_target}% / {eq.performance_target}% / {eq.quality_target}%</TableCell>
                    <TableCell>
                      {eq.next_maintenance_date 
                        ? new Date(eq.next_maintenance_date).toLocaleDateString() 
                        : '-'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
}
