'use client';

import { Box, Typography, Card, CardContent } from '@mui/material';

export default function CustomersPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Customers Management
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Customer management module - Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            This page will allow you to manage customer accounts, contacts, and relationships.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
