'use client';

import { Box, Typography, Card, CardContent } from '@mui/material';

export default function StationsPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Управление станками и станциями
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Настройка станций готовится
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Здесь можно будет настраивать и контролировать производственные станции.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
