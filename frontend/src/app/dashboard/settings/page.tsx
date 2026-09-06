'use client';

import { Box, Typography, Card, CardContent } from '@mui/material';

export default function SettingsPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Tenant Settings
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Tenant configuration settings - Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            This page will allow you to configure tenant-specific settings, preferences, and integrations.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
