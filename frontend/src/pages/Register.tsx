import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { register, login } from '../api/auth';
import { TextField, Button, Box, Typography, Alert } from '@mui/material';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => register(email, password),
    onSuccess: async () => {
      // Auto-login after registration
      const data = await login(email, password);
      localStorage.setItem('token', data.access_token);
      window.location.href = '/';
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Registration failed');
    },
  });

  return (
    <Box maxWidth={400} mx="auto" mt={8}>
      <Typography variant="h4" mb={2}>Register</Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <form onSubmit={e => { e.preventDefault(); mutation.mutate(); }}>
        <TextField
          label="Email"
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          fullWidth
          margin="normal"
          required
        />
        <TextField
          label="Password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          fullWidth
          margin="normal"
          required
        />
        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          disabled={mutation.isPending}
          sx={{ mt: 2 }}
        >
          Register
        </Button>
      </form>
    </Box>
  );
};

export default Register; 