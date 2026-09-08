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
  IconButton,
  Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import ArchiveIcon from '@mui/icons-material/Archive';
import DownloadIcon from '@mui/icons-material/Download';
import VisibilityIcon from '@mui/icons-material/Visibility';
import documentsApi from '@/lib/api/documents';
import type { Document, DocumentCategory, DocumentStats } from '@/types/documents';

export default function DocumentsPage() {
  const [stats, setStats] = useState<DocumentStats | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [categories, setCategories] = useState<DocumentCategory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, docsData, categoriesData] = await Promise.all([
        documentsApi.getDocumentStats(),
        documentsApi.getDocuments({}),
        documentsApi.getCategories({ is_active: true }),
      ]);
      setStats(statsData);
      setDocuments(docsData.slice(0, 15));
      setCategories(categoriesData);
    } catch (error) {
      console.error('Failed to load documents data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'success';
      case 'in_review': return 'warning';
      case 'draft': return 'info';
      case 'obsolete': return undefined;
      case 'archived': return undefined;
      default: return undefined;
    }
  };

  const getCategoryTypeColor = (type: string) => {
    switch (type) {
      case 'technical': return 'primary';
      case 'quality': return 'secondary';
      case 'safety': return 'error';
      case 'process': return 'info';
      default: return undefined;
    }
  };

  if (loading) {
    return <Box sx={{ p: 3 }}><Typography>Loading...</Typography></Box>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Документооборот
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => {}}>
          Новый документ
        </Button>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <DescriptionIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Всего</Typography>
              </Box>
              <Typography variant="h3">{stats?.total_documents || 0}</Typography>
              <Typography color="text.secondary">Документов</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Утверждено</Typography>
              </Box>
              <Typography variant="h3">{stats?.by_status?.approved || 0}</Typography>
              <Typography color="text.secondary">Действующих</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <HourglassEmptyIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">На согласовании</Typography>
              </Box>
              <Typography variant="h3">{stats?.pending_approval || 0}</Typography>
              <Typography color="text.secondary">Ожидают</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <DescriptionIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Черновики</Typography>
              </Box>
              <Typography variant="h3">{stats?.by_status?.draft || 0}</Typography>
              <Typography color="text.secondary">В работе</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ArchiveIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Обязательные</Typography>
              </Box>
              <Typography variant="h3">{stats?.mandatory_count || 0}</Typography>
              <Typography color="text.secondary">Требуются</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Categories Overview */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Категории документов</Typography>
          <Grid container spacing={2}>
            {categories.map((cat) => (
              <Grid item xs={6} sm={4} md={2} key={cat.id}>
                <Chip
                  label={`${cat.name} (${stats?.by_category?.find(c => c.name === cat.name)?.count || 0})`}
                  color={getCategoryTypeColor(cat.category_type) as any}
                  variant="outlined"
                />
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Documents Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Последние документы</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Код</TableCell>
                  <TableCell>Название</TableCell>
                  <TableCell>Категория</TableCell>
                  <TableCell>Версия</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Обязательный</TableCell>
                  <TableCell>Действителен до</TableCell>
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {documents.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell>{doc.code}</TableCell>
                    <TableCell>{doc.title}</TableCell>
                    <TableCell>
                      <Chip
                        label={doc.category?.name || '-'}
                        size="small"
                        color={getCategoryTypeColor(doc.category?.category_type || 'other') as any}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{doc.version}</TableCell>
                    <TableCell>
                      <Chip
                        label={doc.status}
                        size="small"
                        color={getStatusColor(doc.status) as any}
                      />
                    </TableCell>
                    <TableCell>
                      {doc.is_mandatory ? (
                        <Chip label="Да" size="small" color="error" variant="outlined" />
                      ) : (
                        <Typography variant="caption">Нет</Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {doc.effective_date ? new Date(doc.effective_date).toLocaleDateString() : '-'}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Просмотр">
                        <IconButton size="small" onClick={() => {}}>
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Скачать">
                        <IconButton size="small" onClick={() => {}}>
                          <DownloadIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
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
