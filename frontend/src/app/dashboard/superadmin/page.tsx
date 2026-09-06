'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PowerIcon from '@mui/icons-material/Power';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import BlockIcon from '@mui/icons-material/Block';

interface Tenant {
  id: string;
  name: string;
  subdomain: string;
  custom_domain: string | null;
  status: 'active' | 'suspended' | 'pending' | 'trial';
  billing_plan: 'free' | 'startup' | 'professional' | 'enterprise';
  ssl_enabled: boolean;
  admin_email: string | null;
  trial_ends_at: string | null;
  created_at: string;
}

interface TenantStats {
  total_tenants: number;
  active_tenants: number;
  pending_tenants: number;
  suspended_tenants: number;
  trial_tenants: number;
  total_users: number;
  revenue_mrr: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SuperAdminDashboard() {
  const router = useRouter();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [stats, setStats] = useState<TenantStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    subdomain: '',
    custom_domain: '',
    billing_plan: 'free',
    ssl_enabled: false,
    letsencrypt_email: '',
    admin_email: '',
    admin_password: '',
    admin_name: '',
    auto_activate: true,
    trial_days: 14,
  });

  useEffect(() => {
    fetchTenants();
    fetchStats();
  }, []);

  const fetchTenants = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/v1/superadmin/tenants/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setTenants(data.tenants);
      }
    } catch (err) {
      setError('Failed to fetch tenants');
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/v1/superadmin/tenants/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch stats');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (tenant?: Tenant) => {
    if (tenant) {
      setSelectedTenant(tenant);
      setFormData({
        name: tenant.name,
        subdomain: tenant.subdomain,
        custom_domain: tenant.custom_domain || '',
        billing_plan: tenant.billing_plan,
        ssl_enabled: tenant.ssl_enabled,
        letsencrypt_email: '',
        admin_email: tenant.admin_email || '',
        admin_password: '',
        admin_name: '',
        auto_activate: tenant.status === 'active',
        trial_days: 14,
      });
    } else {
      setSelectedTenant(null);
      setFormData({
        name: '',
        subdomain: '',
        custom_domain: '',
        billing_plan: 'free',
        ssl_enabled: false,
        letsencrypt_email: '',
        admin_email: '',
        admin_password: '',
        admin_name: '',
        auto_activate: true,
        trial_days: 14,
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedTenant(null);
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = selectedTenant
        ? `${API_BASE}/api/v1/superadmin/tenants/${selectedTenant.id}`
        : `${API_BASE}/api/v1/superadmin/tenants/`;
      
      const method = selectedTenant ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        handleCloseDialog();
        fetchTenants();
        fetchStats();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Operation failed');
      }
    } catch (err) {
      setError('Failed to save tenant');
    }
  };

  const handleDelete = async (tenantId: string) => {
    if (!confirm('Are you sure you want to delete this tenant?')) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/api/v1/superadmin/tenants/${tenantId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchTenants();
        fetchStats();
      }
    } catch (err) {
      setError('Failed to delete tenant');
    }
  };

  const handleToggleStatus = async (tenantId: string, currentStatus: string) => {
    try {
      const token = localStorage.getItem('token');
      const action = currentStatus === 'active' ? 'suspend' : 'activate';
      const response = await fetch(`${API_BASE}/api/v1/superadmin/tenants/${tenantId}/${action}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        fetchTenants();
        fetchStats();
      }
    } catch (err) {
      setError('Failed to update tenant status');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'suspended': return 'error';
      case 'pending': return 'warning';
      case 'trial': return 'info';
      default: return 'default';
    }
  };

  const getPlanLabel = (plan: string) => {
    switch (plan) {
      case 'free': return 'Free';
      case 'startup': return 'Startup ($29/mo)';
      case 'professional': return 'Professional ($99/mo)';
      case 'enterprise': return 'Enterprise ($299/mo)';
      default: return plan;
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
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          SuperAdmin Dashboard
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Create Tenant
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Tenants
                </Typography>
                <Typography variant="h4">{stats.total_tenants}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Active Tenants
                </Typography>
                <Typography variant="h4" color="success.main">{stats.active_tenants}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Users
                </Typography>
                <Typography variant="h4">{stats.total_users}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Monthly Revenue (MRR)
                </Typography>
                <Typography variant="h4" color="primary.main">${stats.revenue_mrr.toFixed(2)}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tenants Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            All Tenants
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Domain</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Plan</TableCell>
                  <TableCell>SSL</TableCell>
                  <TableCell>Admin</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tenants.map((tenant) => (
                  <TableRow key={tenant.id}>
                    <TableCell>{tenant.name}</TableCell>
                    <TableCell>
                      {tenant.custom_domain || `${tenant.subdomain}.virtuoso-mes.local`}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={tenant.status}
                        color={getStatusColor(tenant.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{getPlanLabel(tenant.billing_plan)}</TableCell>
                    <TableCell>
                      {tenant.ssl_enabled ? (
                        <CheckCircleIcon color="success" fontSize="small" />
                      ) : (
                        <BlockIcon color="disabled" fontSize="small" />
                      )}
                    </TableCell>
                    <TableCell>{tenant.admin_email || '-'}</TableCell>
                    <TableCell>
                      {new Date(tenant.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={() => handleOpenDialog(tenant)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        color={tenant.status === 'active' ? 'error' : 'success'}
                        startIcon={<PowerIcon />}
                        onClick={() => handleToggleStatus(tenant.id, tenant.status)}
                      >
                        {tenant.status === 'active' ? 'Suspend' : 'Activate'}
                      </Button>
                      <Button
                        size="small"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={() => handleDelete(tenant.id)}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedTenant ? 'Edit Tenant' : 'Create New Tenant'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Tenant Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Subdomain"
                  value={formData.subdomain}
                  onChange={(e) => setFormData({ ...formData, subdomain: e.target.value })}
                  required
                  disabled={!!selectedTenant}
                  helperText="Will be used as: subdomain.virtuoso-mes.local"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Custom Domain (optional)"
                  value={formData.custom_domain}
                  onChange={(e) => setFormData({ ...formData, custom_domain: e.target.value })}
                  disabled={!!selectedTenant}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Billing Plan"
                  value={formData.billing_plan}
                  onChange={(e) => setFormData({ ...formData, billing_plan: e.target.value })}
                >
                  <MenuItem value="free">Free</MenuItem>
                  <MenuItem value="startup">Startup ($29/mo)</MenuItem>
                  <MenuItem value="professional">Professional ($99/mo)</MenuItem>
                  <MenuItem value="enterprise">Enterprise ($299/mo)</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="email"
                  label="Let's Encrypt Email"
                  value={formData.letsencrypt_email}
                  onChange={(e) => setFormData({ ...formData, letsencrypt_email: e.target.value })}
                  placeholder="ssl@example.com"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  type="checkbox"
                  label=""
                  checked={formData.ssl_enabled}
                  onChange={(e) => setFormData({ ...formData, ssl_enabled: e.target.checked })}
                  InputProps={{ style: { width: 'auto' } }}
                />
                <label>Enable SSL/TLS</label>
              </Grid>
              {!selectedTenant && (
                <>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      type="email"
                      label="Admin Email"
                      value={formData.admin_email}
                      onChange={(e) => setFormData({ ...formData, admin_email: e.target.value })}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      type="password"
                      label="Admin Password"
                      value={formData.admin_password}
                      onChange={(e) => setFormData({ ...formData, admin_password: e.target.value })}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Admin Name"
                      value={formData.admin_name}
                      onChange={(e) => setFormData({ ...formData, admin_name: e.target.value })}
                    />
                  </Grid>
                </>
              )}
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {selectedTenant ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
