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
  Paper,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import AssessmentIcon from '@mui/icons-material/Assessment';
import WarningIcon from '@mui/icons-material/Warning';
import { LineChart } from '@mui/x-charts/LineChart';
import { PieChart } from '@mui/x-charts/PieChart';
import qualityApi from '@/lib/api/quality';
import type { QualityCheck, DefectType, CorrectiveAction, QualityStats } from '@/types/quality';

export default function QualityPage() {
  const [stats, setStats] = useState<QualityStats | null>(null);
  const [recentChecks, setRecentChecks] = useState<QualityCheck[]>([]);
  const [defectTypes, setDefectTypes] = useState<DefectType[]>([]);
  const [correctiveActions, setCorrectiveActions] = useState<CorrectiveAction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, checksData, defectsData, actionsData] = await Promise.all([
        qualityApi.getQualityStats({ start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], end_date: new Date().toISOString().split('T')[0] }),
        qualityApi.getQualityChecks({ status: 'in_progress' }),
        qualityApi.getDefectTypes({ is_active: true }),
        qualityApi.getCorrectiveActions({ status: 'in_progress' }),
      ]);
      setStats(statsData);
      setRecentChecks(checksData.slice(0, 10));
      setDefectTypes(defectsData);
      setCorrectiveActions(actionsData.slice(0, 5));
    } catch (error) {
      console.error('Failed to load quality data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'minor': return 'info';
      case 'major': return 'warning';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed': return 'success';
      case 'failed': return 'error';
      case 'in_progress': return 'warning';
      case 'pending': return 'info';
      default: return 'default';
    }
  };

  if (loading) {
    return <Box sx={{ p: 3 }}><Typography>Loading...</Typography></Box>;
  }

  const pieData = stats ? [
    { id: 0, value: stats.passed, label: 'Passed', color: '#4caf50' },
    { id: 1, value: stats.failed, label: 'Failed', color: '#f44336' },
  ] : [];

  const defectPieData = defectTypes.length > 0 ? defectTypes.slice(0, 5).map((dt, idx) => ({
    id: idx,
    value: 10, // Placeholder - would need aggregation from backend
    label: dt.name,
  })) : [];

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Управление качеством (ОТК)
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => {}}>
          Новая проверка
        </Button>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AssessmentIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Всего проверок</Typography>
              </Box>
              <Typography variant="h3">{stats?.total_inspections || 0}</Typography>
              <Typography color="text.secondary">За период</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Процент прохождения</Typography>
              </Box>
              <Typography variant="h3">{(stats?.pass_rate || 0).toFixed(1)}%</Typography>
              <Typography color="text.secondary">Успешных: {stats?.passed || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ErrorIcon color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">Всего дефектов</Typography>
              </Box>
              <Typography variant="h3">{stats?.total_defects || 0}</Typography>
              <Typography color="text.secondary">
                Критических: {stats?.defects_by_severity?.critical || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <WarningIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">В работе КА</Typography>
              </Box>
              <Typography variant="h3">{correctiveActions.length}</Typography>
              <Typography color="text.secondary">Корректирующих действий</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Результаты проверок</Typography>
              <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                {pieData.length > 0 && (
                  <PieChart
                    series={[{ data: pieData, innerRadius: 50 }]}
                    width={300}
                    height={300}
                  />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Типы дефектов</Typography>
              <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                {defectPieData.length > 0 && (
                  <PieChart
                    series={[{ data: defectPieData }]}
                    width={300}
                    height={300}
                  />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Checks Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Последние проверки качества</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Тип</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Планировано</TableCell>
                  <TableCell>Проверено</TableCell>
                  <TableCell>Брак</TableCell>
                  <TableCell>Инспектор</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentChecks.map((check) => (
                  <TableRow key={check.id}>
                    <TableCell>{check.id}</TableCell>
                    <TableCell>{check.check_type}</TableCell>
                    <TableCell>
                      <Chip 
                        label={check.status} 
                        size="small" 
                        color={getStatusColor(check.status) as any}
                      />
                    </TableCell>
                    <TableCell>{check.planned_quantity}</TableCell>
                    <TableCell>{check.inspected_quantity}</TableCell>
                    <TableCell>{check.rejected_quantity}</TableCell>
                    <TableCell>{check.inspected_by}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Corrective Actions */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Активные корректирующие действия</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>№</TableCell>
                  <TableCell>Название</TableCell>
                  <TableCell>Приоритет</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Срок</TableCell>
                  <TableCell>Ответственный</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {correctiveActions.map((action) => (
                  <TableRow key={action.id}>
                    <TableCell>{action.request_number}</TableCell>
                    <TableCell>{action.title}</TableCell>
                    <TableCell>
                      <Chip 
                        label={action.priority} 
                        size="small" 
                        color={action.priority === 'urgent' ? 'error' : action.priority === 'high' ? 'warning' : 'default'}
                      />
                    </TableCell>
                    <TableCell>{action.status}</TableCell>
                    <TableCell>{action.due_date ? new Date(action.due_date).toLocaleDateString() : '-'}</TableCell>
                    <TableCell>{action.assigned_to || 'Не назначен'}</TableCell>
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
