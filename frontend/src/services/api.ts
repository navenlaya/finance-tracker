import axios, { AxiosInstance } from 'axios';

// API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-storage');
  if (token) {
    try {
      const authData = JSON.parse(token);
      if (authData.state?.token) {
        config.headers.Authorization = `Bearer ${authData.state.token}`;
      }
    } catch (error) {
      console.error('Error parsing auth token:', error);
    }
  }
  return config;
});

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, clear auth state but don't redirect
      // The App component will handle the redirect based on auth state
      localStorage.removeItem('auth-storage');
    }
    return Promise.reject(error);
  }
);

// API Response Types
interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    first_name?: string;
    last_name?: string;
    has_plaid_connection: boolean;
  };
}



interface Account {
  id: string;
  account_name: string;
  account_type: string;
  current_balance?: number;
  available_balance?: number;
  institution_name?: string;
  mask?: string;
  last_sync?: string;
}

interface Transaction {
  id: string;
  amount: number;
  name: string;
  date: string;
  category?: string[];
  customCategory?: string;
  merchantName?: string;
  transactionType: string;
  pending: boolean;
  accountId: string;
}

interface PlaidConnection {
  is_connected?: boolean;
  institution_name?: string;
  accounts_count?: number;
  last_sync?: string;
}

interface Budget {
  id: string;
  name: string;
  category: string;
  budgetLimit: number;
  periodType: string;
  startDate: string;
  endDate: string;
  alertThreshold: number;
  autoRollover: boolean;
  spentAmount: number;
  remainingAmount: number;
  utilizationPercentage: number;
  isOverBudget: boolean;
  shouldAlert: boolean;
  isActive: boolean;
}

// Auth API
export const authApi = {
  login: async (credentials: { email: string; password: string }): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: {
    email: string;
    password: string;
    firstName?: string;
    lastName?: string;
  }): Promise<LoginResponse> => {
    // Convert camelCase to snake_case for backend
    const backendData = {
      email: userData.email,
      password: userData.password,
      first_name: userData.firstName,
      last_name: userData.lastName,
    };
    const response = await apiClient.post('/auth/register', backendData);
    return response.data;
  },

  refreshToken: async (): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/refresh');
    return response.data;
  },

  getCurrentUser: async (): Promise<{
    id: string;
    email: string;
    first_name?: string;
    last_name?: string;
    has_plaid_connection: boolean;
  }> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

// Plaid API
export const plaidApi = {
  createLinkToken: async (): Promise<{ link_token: string }> => {
    const response = await apiClient.post('/plaid/create-link-token');
    return response.data;
  },

  exchangePublicToken: async (data: {
    public_token: string;
    institution_id: string;
    institution_name: string;
  }): Promise<{ message: string; accounts_connected: number }> => {
    const response = await apiClient.post('/plaid/exchange-public-token', data);
    return response.data;
  },

  getConnectionStatus: async (): Promise<PlaidConnection> => {
    const response = await apiClient.get('/plaid/connection-status');
    return response.data;
  },

  syncAccounts: async (): Promise<{ message: string; accounts_synced: number }> => {
    const response = await apiClient.post('/plaid/sync-accounts');
    return response.data;
  },

  syncTransactions: async (daysBack: number = 30): Promise<{ message: string; transactions_synced: number }> => {
    const response = await apiClient.post('/plaid/sync-transactions', { days_back: daysBack });
    return response.data;
  },

  disconnect: async (): Promise<{ message: string }> => {
    const response = await apiClient.delete('/plaid/disconnect');
    return response.data;
  },
};

// Accounts API
export const accountsApi = {
  getAccounts: async (): Promise<Account[]> => {
    const response = await apiClient.get('/accounts');
    return response.data;
  },

  getAccount: async (accountId: string): Promise<Account> => {
    const response = await apiClient.get(`/accounts/${accountId}`);
    return response.data;
  },
};

// Transactions API
export const transactionsApi = {
  getTransactions: async (params?: {
    limit?: number;
    offset?: number;
    accountId?: string;
    category?: string;
    startDate?: string;
    endDate?: string;
  }): Promise<Transaction[]> => {
    const response = await apiClient.get('/transactions', { params });
    return response.data;
  },

  getDashboardData: async (): Promise<{
    totalBalance: number;
    monthlyIncome: number;
    monthlyExpenses: number;
    monthlySavings: number;
    accountSummary: Account[];
    recentTransactions: Transaction[];
    spendingByCategory: Array<{ category: string; amount: number; percentage: number }>;
  }> => {
    const response = await apiClient.get('/transactions/dashboard');
    return response.data;
  },

  createTransaction: async (transactionData: {
    accountId: string;
    amount: number;
    name: string;
    date: string;
    transactionType: string;
    customCategory?: string;
    notes?: string;
  }): Promise<Transaction> => {
    const response = await apiClient.post('/transactions', transactionData);
    return response.data;
  },

  updateTransaction: async (transactionId: string, updates: {
    customCategory?: string;
    notes?: string;
    tags?: string[];
  }): Promise<Transaction> => {
    const response = await apiClient.put(`/transactions/${transactionId}`, updates);
    return response.data;
  },
};

// Budgets API
export const budgetsApi = {
  getBudgets: async (): Promise<Budget[]> => {
    const response = await apiClient.get('/budgets');
    return response.data;
  },

  createBudget: async (budgetData: {
    name: string;
    category: string;
    budgetLimit: number;
    periodType: string;
    startDate: string;
    endDate: string;
    alertThreshold: number;
    autoRollover: boolean;
  }): Promise<Budget> => {
    const response = await apiClient.post('/budgets', budgetData);
    return response.data;
  },

  updateBudget: async (budgetData: {
    id: string;
    name?: string;
    category?: string;
    budgetLimit?: number;
    periodType?: string;
    startDate?: string;
    endDate?: string;
    alertThreshold?: number;
    autoRollover?: boolean;
  }): Promise<Budget> => {
    const { id, ...data } = budgetData;
    const response = await apiClient.put(`/budgets/${id}`, data);
    return response.data;
  },

  deleteBudget: async (budgetId: string): Promise<void> => {
    await apiClient.delete(`/budgets/${budgetId}`);
  },
};

// ML API
export const mlApi = {
  getForecast: async (daysAhead: number = 30): Promise<Array<{
    category: string;
    forecastAmount: number;
    confidenceIntervalLower: number;
    confidenceIntervalUpper: number;
    forecastDate: string;
    trend: string;
  }>> => {
    const response = await apiClient.get('/ml/forecast', { params: { days_ahead: daysAhead } });
    return response.data;
  },

  getInsights: async (): Promise<Array<{
    insightType: string;
    title: string;
    description: string;
    category?: string;
    confidenceScore: number;
    createdAt: string;
  }>> => {
    const response = await apiClient.get('/ml/insights');
    return response.data;
  },

  retrainModels: async (): Promise<{ message: string }> => {
    const response = await apiClient.post('/ml/retrain');
    return response.data;
  },
}; 