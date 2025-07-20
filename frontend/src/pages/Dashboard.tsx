import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Button, Box, Typography, CircularProgress, Alert, List, ListItem, ListItemText, Divider, TextField, Paper } from '@mui/material';
import { usePlaidLink } from 'react-plaid-link';
import api from '../api/client';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

const fetchLinkToken = async () => {
  const res = await api.get('/plaid/link-token');
  return res.data.link_token;
};

const fetchAccounts = async () => {
  const res = await api.get('/plaid/accounts');
  return res.data.accounts;
};

const fetchTransactions = async () => {
  const res = await api.get('/plaid/transactions');
  return res.data.transactions;
};

const fetchForecast = async () => {
  const res = await api.get('/ml/forecast');
  return res.data.forecast;
};

const removeAccount = async (item_id: string) => {
  await api.delete(`/plaid/remove-account`, { params: { item_id } });
};

const Dashboard: React.FC = () => {
  const { data: linkToken, isLoading: loadingToken, error: errorToken } = useQuery({
    queryKey: ['linkToken'],
    queryFn: fetchLinkToken,
  });

  const { data: accounts, isLoading: loadingAccounts, error: errorAccounts, refetch: refetchAccounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: fetchAccounts,
  });

  const { data: transactions, isLoading: loadingTxns, error: errorTxns, refetch: refetchTxns } = useQuery({
    queryKey: ['transactions'],
    queryFn: fetchTransactions,
  });

  const { data: forecast, isLoading: loadingForecast, error: errorForecast, refetch: refetchForecast } = useQuery({
    queryKey: ['forecast'],
    queryFn: fetchForecast,
  });

  const onSuccess = React.useCallback((public_token: string, metadata: any) => {
    api.post('/plaid/exchange', { public_token })
      .then(() => {
        refetchAccounts();
        refetchTxns();
        refetchForecast();
      })
      .catch(() => alert('Token exchange failed'));
  }, [refetchAccounts, refetchTxns, refetchForecast]);

  const config = {
    token: linkToken,
    onSuccess,
  };

  const { open, ready } = usePlaidLink(config);

  const removeMutation = useMutation({
    mutationFn: removeAccount,
    onSuccess: () => {
      refetchAccounts();
    },
  });

  // Prepare forecast chart data
  const chartData = forecast ? {
    labels: forecast.map((f: any) => f.ds),
    datasets: [
      {
        label: 'Forecasted Spending',
        data: forecast.map((f: any) => f.yhat),
        borderColor: 'rgba(75,192,192,1)',
        fill: false,
      },
      {
        label: 'Lower Bound',
        data: forecast.map((f: any) => f.yhat_lower),
        borderColor: 'rgba(192,75,75,0.5)',
        borderDash: [5, 5],
        fill: false,
      },
      {
        label: 'Upper Bound',
        data: forecast.map((f: any) => f.yhat_upper),
        borderColor: 'rgba(75,75,192,0.5)',
        borderDash: [5, 5],
        fill: false,
      },
    ],
  } : undefined;

  return (
    <Box maxWidth={900} mx="auto" mt={8}>
      <Typography variant="h4" mb={2}>Dashboard</Typography>
      {loadingToken && <CircularProgress />}
      {errorToken && <Alert severity="error">Failed to load Plaid Link token</Alert>}
      {linkToken && (
        <Button
          variant="contained"
          color="primary"
          onClick={() => open()}
          disabled={!ready}
          sx={{ mb: 4 }}
        >
          Connect Bank Account
        </Button>
      )}
      <Divider sx={{ my: 4 }} />
      <Typography variant="h6">Spending Forecast</Typography>
      {loadingForecast && <CircularProgress />}
      {errorForecast && <Alert severity="error">Failed to load forecast</Alert>}
      {forecast && (
        <Paper sx={{ p: 2, mb: 4 }}>
          <Line data={chartData!} />
        </Paper>
      )}
      <Divider sx={{ my: 4 }} />
      <Typography variant="h6">Linked Accounts</Typography>
      {loadingAccounts && <CircularProgress />}
      {errorAccounts && <Alert severity="error">Failed to load accounts</Alert>}
      <List>
        {accounts && accounts.map((acct: any) => (
          <ListItem key={acct.account_id} secondaryAction={
            acct.item_id && (
              <Button
                color="error"
                variant="outlined"
                size="small"
                onClick={() => removeMutation.mutate(acct.item_id)}
              >
                Remove
              </Button>
            )
          }>
            <ListItemText primary={acct.name} secondary={acct.official_name || acct.subtype} />
          </ListItem>
        ))}
      </List>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h6">Recent Transactions</Typography>
      {loadingTxns && <CircularProgress />}
      {errorTxns && <Alert severity="error">Failed to load transactions</Alert>}
      <List>
        {transactions && transactions.map((txn: any) => (
          <ListItem key={txn.transaction_id}>
            <ListItemText
              primary={`${txn.name} - $${txn.amount}`}
              secondary={txn.date}
            />
          </ListItem>
        ))}
      </List>
      <Divider sx={{ my: 4 }} />
    </Box>
  );
};

export default Dashboard; 