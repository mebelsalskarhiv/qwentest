'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
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
} from '@mui/material';

export default function LoginPage() {
  const router = useRouter();
  const { login, setUser } = useAuthStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authApi.login(username, password);
      const { access_token, refresh_token } = response.data;
      
      login(access_token, refresh_token);
      
      // Get user info
      const userResponse = await authApi.getMe();
      setUser(userResponse.data);
      
      router.push('/dashboard');
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Login failed. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Virtuoso MES
          </Typography>
          <Typography variant="subtitle1" color="textSecondary" align="center" gutterBottom>
            Manufacturing Execution System
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              required
              autoComplete="username"
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
              autoComplete="current-password"
            />
            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, mb: 2 }}
            >
              {loading ? 'Logging in...' : 'Login'}
            </Button>
            
            <Typography variant="caption" color="textSecondary" align="center" display="block">
              Default credentials: admin / admin123
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
