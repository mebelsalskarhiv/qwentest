'use client';

import { Box, Typography, Card, CardContent } from '@mui/material';

export default function ReportsPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Отчёты и аналитика
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Панель отчётов и аналитики готовится
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Здесь будут доступны сводные показатели производства, склада и персонала.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
