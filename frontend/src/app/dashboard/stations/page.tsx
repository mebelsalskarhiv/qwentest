'use client';

import { Box, Typography, Card, CardContent } from '@mui/material';

export default function StationsPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Work Stations Management
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Work stations configuration - Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            This page will allow you to configure and monitor production work stations.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
