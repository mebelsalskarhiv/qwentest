'use client';

import { Box, Typography, Card, CardContent } from '@mui/material';

export default function CustomersPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Управление клиентами
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Модуль управления клиентами готовится
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Здесь будут доступны счета клиентов, контактные лица и история взаимодействия.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
