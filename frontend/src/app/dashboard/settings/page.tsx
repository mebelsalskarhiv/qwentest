'use client';

import { Box, Typography, Card, CardContent } from '@mui/material';

export default function SettingsPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Настройки тенанта
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Настройки тенанта готовятся
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Здесь можно будет настроить параметры, предпочтения и интеграции тенанта.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
