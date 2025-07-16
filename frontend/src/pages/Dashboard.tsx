import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button, Box, Typography, CircularProgress, Alert } from '@mui/material';
import { usePlaidLink } from 'react-plaid-link';
import api from '../api/client';

const fetchLinkToken = async () => {
  const res = await api.get('/plaid/link-token');
  return res.data.link_token;
};

const Dashboard: React.FC = () => {
  const { data: linkToken, isLoading, error } = useQuery({
    queryKey: ['linkToken'],
    queryFn: fetchLinkToken,
  });

  const onSuccess = React.useCallback((public_token: string, metadata: any) => {
    // Exchange public_token for access_token
    api.post('/plaid/exchange', { public_token })
      .then(() => window.location.reload())
      .catch(() => alert('Token exchange failed'));
  }, []);

  const config = {
    token: linkToken,
    onSuccess,
  };

  const { open, ready } = usePlaidLink(config);

  return (
    <Box maxWidth={600} mx="auto" mt={8}>
      <Typography variant="h4" mb={2}>Dashboard</Typography>
      {isLoading && <CircularProgress />}
      {error && <Alert severity="error">Failed to load Plaid Link token</Alert>}
      {linkToken && (
        <Button
          variant="contained"
          color="primary"
          onClick={() => open()}
          disabled={!ready}
        >
          Connect Bank Account
        </Button>
      )}
    </Box>
  );
};

export default Dashboard; 