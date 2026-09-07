'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Alert, Box, Button, Chip, Container, Grid, Paper, Stack, TextField, Typography } from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import FactoryIcon from '@mui/icons-material/Factory';
import InsightsIcon from '@mui/icons-material/Insights';
import Inventory2Icon from '@mui/icons-material/Inventory2';
import ShieldIcon from '@mui/icons-material/Shield';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';

const capabilities = [
  { icon: <FactoryIcon />, title: 'Производство', text: 'Заказы, этапы и Kanban-поток в одном рабочем пространстве.' },
  { icon: <Inventory2Icon />, title: 'Склад', text: 'Остатки, материалы и резервы всегда перед глазами команды.' },
  { icon: <InsightsIcon />, title: 'Показатели', text: 'Данные для решений руководителя без ручных сводок.' },
  { icon: <ShieldIcon />, title: 'Изоляция данных', text: 'Каждый tenant работает в собственном защищённом контуре.' },
];

export default function LoginPage() {
  const router = useRouter();
  const { login, setUser } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [registrationMessage, setRegistrationMessage] = useState('');
  const [registration, setRegistration] = useState({ tenant_name: '', subdomain: '', email: '', username: '', password: '', full_name: '' });

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
      setError(err.response?.data?.detail || 'Не удалось открыть демо-режим.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegistration = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setRegistrationMessage('');
    setLoading(true);
    try {
      const response = await authApi.registerTenant(registration);
      login(response.data.access_token, response.data.refresh_token);
      setUser(response.data.user);
      setRegistrationMessage('Рабочее пространство создано. Открываем кабинет...');
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Не удалось создать рабочее пространство.');
    } finally {
      setLoading(false);
    }
  };

  const updateRegistration = (field: string, value: string) => setRegistration((current) => ({ ...current, [field]: value }));

  return (
    <Box sx={{ minHeight: '100vh', color: '#15352e', background: 'radial-gradient(circle at 85% 8%, rgba(91,194,165,.25), transparent 32%), #f4f7f5' }}>
      <Box component="header" sx={{ py: 2.5 }}>
        <Container maxWidth="lg" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Stack direction="row" spacing={1.2} alignItems="center">
            <Box sx={{ width: 38, height: 38, borderRadius: 2, display: 'grid', placeItems: 'center', bgcolor: 'primary.main', color: 'white' }}><FactoryIcon /></Box>
            <Typography variant="h6" fontWeight={800}>Virtuoso MES</Typography>
          </Stack>
          <Button variant="text" onClick={() => router.push('/superadmin/login')}>Вход администратора платформы</Button>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ pt: { xs: 5, md: 10 }, pb: 10 }}>
        <Grid container spacing={{ xs: 5, md: 9 }} alignItems="center">
          <Grid item xs={12} md={7}>
            <Chip label="MES нового поколения" sx={{ mb: 3, bgcolor: '#d9eee7', color: 'primary.dark', fontWeight: 800 }} />
            <Typography variant="h1" sx={{ fontSize: { xs: '3.2rem', md: '5.8rem' }, lineHeight: .98, maxWidth: 760 }}>
              Производство, которое видно целиком.
            </Typography>
            <Typography variant="h6" sx={{ mt: 3, maxWidth: 620, color: '#5b716a', lineHeight: 1.55, fontWeight: 500 }}>
              Virtuoso MES соединяет цех, склад и управленческие решения в одном понятном интерфейсе.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mt: 5 }}>
              <Button size="large" variant="contained" endIcon={<ArrowForwardIcon />} onClick={handleDemoLogin} disabled={loading} sx={{ px: 3, py: 1.5 }}>
                {loading ? 'Открываем демо...' : 'Открыть демо-производство'}
              </Button>
              <Button size="large" variant="outlined" href="#register" sx={{ px: 3, py: 1.5 }}>Создать свой tenant</Button>
            </Stack>
            <Typography variant="body2" sx={{ mt: 2, color: '#789088' }}>Демо-данные уже загружены: заказы, склад, сотрудники и станции.</Typography>
          </Grid>

          <Grid item xs={12} md={5}>
            <Paper sx={{ p: { xs: 3, md: 4 }, borderRadius: 4, bgcolor: '#123d35', color: 'white', position: 'relative', overflow: 'hidden' }}>
              <Box sx={{ position: 'absolute', width: 180, height: 180, borderRadius: '50%', bgcolor: 'rgba(91,194,165,.18)', top: -80, right: -50 }} />
              <Typography variant="overline" sx={{ color: '#8ee0c5', fontWeight: 800, letterSpacing: '.14em' }}>РАБОЧЕЕ ПРОСТРАНСТВО</Typography>
              <Typography variant="h4" sx={{ mt: 2, fontWeight: 800 }}>Всё, что важно смене</Typography>
              <Stack spacing={2} sx={{ mt: 4 }}>
                {['Статусы заказов в реальном времени', 'Единый поток задач для цеха', 'Контроль материалов и сроков'].map((item) => (
                  <Stack direction="row" spacing={1.5} alignItems="center" key={item}>
                    <Box sx={{ width: 9, height: 9, borderRadius: '50%', bgcolor: '#69d4b1' }} />
                    <Typography>{item}</Typography>
                  </Stack>
                ))}
              </Stack>
              <Box sx={{ mt: 5, p: 2, borderRadius: 2, bgcolor: 'rgba(255,255,255,.09)' }}>
                <Typography variant="caption" sx={{ color: '#9cc8bc' }}>ДЕМО TENANT</Typography>
                <Typography variant="h6" sx={{ mt: .5 }}>Демо-производство</Typography>
                <Typography variant="body2" sx={{ color: '#b9d4cc' }}>Готово к исследованию</Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        <Grid container spacing={2} sx={{ mt: { xs: 7, md: 12 } }}>
          {capabilities.map((item) => (
            <Grid item xs={12} sm={6} md={3} key={item.title}>
              <Paper sx={{ p: 2.5, height: '100%', borderRadius: 3 }}>
                <Box sx={{ color: 'secondary.main', mb: 2 }}>{item.icon}</Box>
                <Typography variant="h6" fontWeight={800}>{item.title}</Typography>
                <Typography variant="body2" sx={{ mt: 1, color: '#6b8079', lineHeight: 1.55 }}>{item.text}</Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        <Paper id="register" sx={{ mt: 10, p: { xs: 3, md: 5 }, borderRadius: 4 }}>
          <Grid container spacing={5} alignItems="center">
            <Grid item xs={12} md={5}>
              <Typography variant="overline" color="secondary.main" fontWeight={800}>СТАРТ ЗА 2 МИНУТЫ</Typography>
              <Typography variant="h3" sx={{ mt: 1 }}>Создайте своё пространство</Typography>
              <Typography sx={{ mt: 2, color: '#6b8079' }}>Отдельный tenant для вашей команды с собственным администратором и данными.</Typography>
            </Grid>
            <Grid item xs={12} md={7}>
              {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
              {registrationMessage && <Alert severity="success" sx={{ mb: 2 }}>{registrationMessage}</Alert>}
              <Box component="form" onSubmit={handleRegistration}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}><TextField fullWidth required label="Название компании" value={registration.tenant_name} onChange={(e) => updateRegistration('tenant_name', e.target.value)} /></Grid>
                  <Grid item xs={12} sm={6}><TextField fullWidth required label="Поддомен" helperText="латиница, цифры и дефис" value={registration.subdomain} onChange={(e) => updateRegistration('subdomain', e.target.value.toLowerCase())} /></Grid>
                  <Grid item xs={12} sm={6}><TextField fullWidth required type="email" label="Email" value={registration.email} onChange={(e) => updateRegistration('email', e.target.value)} /></Grid>
                  <Grid item xs={12} sm={6}><TextField fullWidth required label="Имя пользователя" value={registration.username} onChange={(e) => updateRegistration('username', e.target.value)} /></Grid>
                  <Grid item xs={12} sm={6}><TextField fullWidth label="Ваше имя" value={registration.full_name} onChange={(e) => updateRegistration('full_name', e.target.value)} /></Grid>
                  <Grid item xs={12} sm={6}><TextField fullWidth required type="password" label="Пароль" inputProps={{ minLength: 8 }} value={registration.password} onChange={(e) => updateRegistration('password', e.target.value)} /></Grid>
                  <Grid item xs={12}><Button fullWidth type="submit" variant="contained" size="large" disabled={loading}>Создать рабочее пространство</Button></Grid>
                </Grid>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Container>
    </Box>
  );
}
