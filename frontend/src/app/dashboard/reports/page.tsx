'use client';

import { Box, Typography, Card, CardContent } from '@mui/material';

export default function ReportsPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Reports & Analytics
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Reports and analytics dashboard - Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            This page will provide comprehensive reports on production, inventory, and HR metrics.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
