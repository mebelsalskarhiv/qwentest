'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Alert, Box, Button, Container, Paper, TextField, Typography } from '@mui/material';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';

export default function SuperadminLoginPage() {
  const router = useRouter();
  const { login, setUser } = useAuthStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authApi.superadminLogin(username, password);
      login(response.data.access_token, response.data.refresh_token);
      const userResponse = await authApi.getMe();
      setUser(userResponse.data);
      router.push('/dashboard/superadmin');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Superadmin login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 12 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Superadmin login
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 3 }}>
          This entry is reserved for platform tenant management.
        </Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Box component="form" onSubmit={handleSubmit}>
          <TextField fullWidth label="Username or email" required margin="normal" value={username} onChange={(e) => setUsername(e.target.value)} />
          <TextField fullWidth label="Password" type="password" required margin="normal" value={password} onChange={(e) => setPassword(e.target.value)} />
          <Button fullWidth type="submit" variant="contained" disabled={loading} sx={{ mt: 3 }}>
            {loading ? 'Signing in...' : 'Sign in as superadmin'}
          </Button>
          <Button fullWidth variant="text" onClick={() => router.push('/')} sx={{ mt: 1 }}>
            Back to demo
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}