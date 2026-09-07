'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import FactoryIcon from '@mui/icons-material/Factory';
import SpeedIcon from '@mui/icons-material/Speed';
import SecurityIcon from '@mui/icons-material/Security';
import CloudIcon from '@mui/icons-material/Cloud';

export default function LoginPage() {
  const router = useRouter();
  const { login, setUser } = useAuthStore();
  const [registration, setRegistration] = useState({
    tenant_name: '',
    subdomain: '',
    email: '',
    username: '',
    password: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const [registrationMessage, setRegistrationMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDemoLogin = async () => {
    setError('');
    setLoading(true);

    try {
      const response = await authApi.demoLogin();
      login(response.data.access_token, response.data.refresh_token);
      const userResponse = await authApi.getMe();
      setUser(userResponse.data);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Demo mode is temporarily unavailable.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegistration = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setRegistrationMessage('');
    setLoading(true);

    try {
      const response = await authApi.registerTenant(registration);
      login(response.data.access_token, response.data.refresh_token);
      setUser(response.data.user);
      setRegistrationMessage('Tenant created. Opening your workspace...');
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to create tenant.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
          color: 'white',
          py: 8,
          px: 3,
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
                Virtuoso MES
              </Typography>
              <Typography variant="h5" gutterBottom>
                Modern Manufacturing Execution System
              </Typography>
              <Typography variant="body1" sx={{ mt: 2, opacity: 0.9 }}>
                Streamline your production, manage inventory, and optimize workflows with our cloud-native multi-tenant MES platform.
              </Typography>
              
              <Box sx={{ mt: 4 }}>
                <Button
                  variant="contained"
                  size="large"
                  sx={{ mr: 2, bgcolor: 'white', color: 'primary.main' }}
                  onClick={() => router.push('#register')}
                >
                  Start Free Trial
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  sx={{ color: 'white', borderColor: 'white' }}
                  onClick={() => window.open('https://virtuoso-mes.local/docs', '_blank')}
                >
                  Learn More
                </Button>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper elevation={4} sx={{ p: 3 }}>
                <Typography variant="h5" component="h2" gutterBottom align="center">
                  Demo workspace
                </Typography>
                
                {error && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                  </Alert>
                )}

                <Box sx={{ mt: 2 }}>
                  <Button
                    fullWidth
                    variant="contained"
                    size="large"
                    disabled={loading}
                    onClick={handleDemoLogin}
                    sx={{ mt: 3, mb: 2 }}
                  >
                    {loading ? 'Opening demo...' : 'Enter demo mode'}
                  </Button>
                  <Typography variant="body2" color="text.secondary" align="center" display="block">
                    Demo data is isolated in the `demo` tenant.
                  </Typography>
                  <Button fullWidth variant="text" onClick={() => router.push('/superadmin/login')} sx={{ mt: 2 }}>
                    Superadmin login
                  </Button>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container id="register" maxWidth="sm" sx={{ py: 8 }}>
        <Typography variant="h4" component="h2" gutterBottom align="center">
          Create a tenant
        </Typography>
        <Typography color="text.secondary" align="center" sx={{ mb: 3 }}>
          Start an isolated workspace with its own administrator.
        </Typography>
        {registrationMessage && <Alert severity="success" sx={{ mb: 2 }}>{registrationMessage}</Alert>}
        <Box component="form" onSubmit={handleRegistration}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField fullWidth label="Company name" required value={registration.tenant_name} onChange={(e) => setRegistration({ ...registration, tenant_name: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Subdomain" required helperText="3+ lowercase letters, numbers or hyphens" value={registration.subdomain} onChange={(e) => setRegistration({ ...registration, subdomain: e.target.value.toLowerCase() })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Your name" value={registration.full_name} onChange={(e) => setRegistration({ ...registration, full_name: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth type="email" label="Email" required value={registration.email} onChange={(e) => setRegistration({ ...registration, email: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Username" required value={registration.username} onChange={(e) => setRegistration({ ...registration, username: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth type="password" label="Password" required inputProps={{ minLength: 8 }} value={registration.password} onChange={(e) => setRegistration({ ...registration, password: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <Button fullWidth type="submit" variant="outlined" size="large" disabled={loading}>
                Create tenant account
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Container>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h4" component="h2" gutterBottom align="center" sx={{ mb: 6 }}>
          Why Choose Virtuoso MES?
        </Typography>
        
        <Grid container spacing={4}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <FactoryIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Production Management
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Track work orders, manage BOMs, and monitor production in real-time.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <SpeedIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Inventory Control
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Real-time inventory tracking across multiple warehouses and locations.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <SecurityIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Secure & Isolated
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Multi-tenant architecture with complete data isolation and SSL encryption.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <CloudIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Cloud Native
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Deploy anywhere with Docker. Automatic SSL with Let's Encrypt.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Pricing Section */}
      <Container maxWidth="lg" sx={{ py: 8, bgcolor: 'grey.50' }}>
        <Typography variant="h4" component="h2" gutterBottom align="center" sx={{ mb: 6 }}>
          Simple, Transparent Pricing
        </Typography>
        
        <Grid container spacing={4} justifyContent="center">
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h6" color="text.secondary">Free</Typography>
                <Typography variant="h3" color="primary.main" sx={{ my: 2 }}>$0</Typography>
                <Typography variant="body2" color="text.secondary">per month</Typography>
                <Typography variant="body2" sx={{ mt: 2 }}>Up to 5 users</Typography>
                <Typography variant="body2">Basic features</Typography>
                <Button fullWidth variant="outlined" sx={{ mt: 3 }}>Get Started</Button>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', textAlign: 'center', border: 2, borderColor: 'primary.main' }}>
              <CardContent>
                <Typography variant="h6" color="primary.main">Startup</Typography>
                <Typography variant="h3" color="primary.main" sx={{ my: 2 }}>$29</Typography>
                <Typography variant="body2" color="text.secondary">per month</Typography>
                <Typography variant="body2" sx={{ mt: 2 }}>Up to 20 users</Typography>
                <Typography variant="body2">Advanced features</Typography>
                <Button fullWidth variant="contained" sx={{ mt: 3 }}>Start Trial</Button>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h6" color="text.secondary">Professional</Typography>
                <Typography variant="h3" color="primary.main" sx={{ my: 2 }}>$99</Typography>
                <Typography variant="body2" color="text.secondary">per month</Typography>
                <Typography variant="body2" sx={{ mt: 2 }}>Up to 100 users</Typography>
                <Typography variant="body2">All features</Typography>
                <Button fullWidth variant="outlined" sx={{ mt: 3 }}>Start Trial</Button>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h6" color="text.secondary">Enterprise</Typography>
                <Typography variant="h3" color="primary.main" sx={{ my: 2 }}>$299</Typography>
                <Typography variant="body2" color="text.secondary">per month</Typography>
                <Typography variant="body2" sx={{ mt: 2 }}>Unlimited users</Typography>
                <Typography variant="body2">Custom integrations</Typography>
                <Button fullWidth variant="outlined" sx={{ mt: 3 }}>Contact Sales</Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Footer */}
      <Box sx={{ bgcolor: 'grey.900', color: 'white', py: 4 }}>
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>Virtuoso MES</Typography>
              <Typography variant="body2" color="grey.400">
                Modern Manufacturing Execution System for smart factories.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>Quick Links</Typography>
              <Link href="/docs" style={{ color: 'inherit', textDecoration: 'none' }}>
                <Typography variant="body2" color="grey.400">Documentation</Typography>
              </Link>
              <Link href="/api/docs" style={{ color: 'inherit', textDecoration: 'none' }}>
                <Typography variant="body2" color="grey.400">API Reference</Typography>
              </Link>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>Contact</Typography>
              <Typography variant="body2" color="grey.400">
                Email: support@virtuoso-mes.local
              </Typography>
            </Grid>
          </Grid>
          <Typography variant="body2" color="grey.500" align="center" sx={{ mt: 4 }}>
            © 2024 Virtuoso MES. All rights reserved.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}
