import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button, Box, Typography, CircularProgress, Alert, List, ListItem, ListItemText, Divider } from '@mui/material';
import { usePlaidLink } from 'react-plaid-link';
import api from '../api/client';

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

  const onSuccess = React.useCallback((public_token: string, metadata: any) => {
    api.post('/plaid/exchange', { public_token })
      .then(() => {
        refetchAccounts();
        refetchTxns();
      })
      .catch(() => alert('Token exchange failed'));
  }, [refetchAccounts, refetchTxns]);

  const config = {
    token: linkToken,
    onSuccess,
  };

  const { open, ready } = usePlaidLink(config);

  return (
    <Box maxWidth={800} mx="auto" mt={8}>
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
      <Typography variant="h6">Linked Accounts</Typography>
      {loadingAccounts && <CircularProgress />}
      {errorAccounts && <Alert severity="error">Failed to load accounts</Alert>}
      <List>
        {accounts && accounts.map((acct: any) => (
          <ListItem key={acct.account_id}>
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
    </Box>
  );
};

export default Dashboard; 