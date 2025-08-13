import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  TrendingUp, 
  TrendingDown, 
  Search, 
  Download,
  Plus,
  Calendar,
  CreditCard
} from 'lucide-react';
import { transactionsApi, accountsApi } from '../services/api';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

export const Transactions: React.FC = () => {
  console.log('Transactions component rendering...');
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAccount, setSelectedAccount] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [dateRange, setDateRange] = useState<string>('30');



  // Fetch transactions data - simplified for now
  const { data: transactions, isLoading, error } = useQuery(
    'transactions',
    () => transactionsApi.getTransactions({ limit: 100 }),
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );

  // Fetch accounts for filter
  const { data: accounts } = useQuery(
    'accounts',
    accountsApi.getAccounts,
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );



  function getCategoryIcon(category: string[] | undefined): React.ReactNode {
    if (category?.includes('food') || category?.includes('restaurant')) {
      return <span className="text-orange-500">🍽️</span>;
    } else if (category?.includes('transport') || category?.includes('travel')) {
      return <span className="text-blue-500">🚗</span>;
    } else if (category?.includes('shopping')) {
      return <span className="text-purple-500">🛍️</span>;
    } else if (category?.includes('entertainment')) {
      return <span className="text-pink-500">🎬</span>;
    } else if (category?.includes('health')) {
      return <span className="text-green-500">🏥</span>;
    } else {
      return <span className="text-gray-500">💰</span>;
    }
  }

  function formatAmount(amount: number): string {
    // TEMPORARY FIX: Reverse the logic since the data seems backwards
    // In a real system, this should use transaction_type from the backend
    const isExpense = amount > 0; // Changed from < 0 to > 0
    const absAmount = Math.abs(amount);
    return `${isExpense ? '-' : '+'}$${absAmount.toFixed(2)}`;
  }

  function getAmountColor(amount: number): string {
    // TEMPORARY FIX: Reverse the color logic to match the reversed amount logic
    // In a real system, this should use transaction_type from the backend
    return amount > 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400';
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Error Loading Transactions
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {error instanceof Error ? error.message : 'An unexpected error occurred'}
          </p>
          <Button 
            variant="outline"
            onClick={() => window.location.reload()}
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Transactions
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            View and manage your transaction history
          </p>
        </div>

        <div className="flex space-x-3">
          <Button variant="outline" size="md">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="primary" size="md">
            <Plus className="h-4 w-4 mr-2" />
            Add Transaction
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search transactions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Account Filter */}
          <select
            value={selectedAccount}
            onChange={(e) => setSelectedAccount(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Accounts</option>
            {accounts?.map((account) => (
              <option key={account.id} value={account.id}>
                {account.account_name}
              </option>
            ))}
          </select>

          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Categories</option>
            <option value="food">Food & Dining</option>
            <option value="transport">Transportation</option>
            <option value="shopping">Shopping</option>
            <option value="entertainment">Entertainment</option>
            <option value="health">Health & Fitness</option>
            <option value="utilities">Utilities</option>
            <option value="income">Income</option>
          </select>

          {/* Date Range */}
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
        </div>
      </div>

      {/* Transactions List */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Transaction</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Category</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Account</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Date</th>
                <th className="text-right py-3 px-4 font-medium text-gray-900 dark:text-white">Amount</th>
              </tr>
            </thead>
            <tbody>
              {transactions?.map((transaction) => (
                <tr key={transaction.id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="py-4 px-4">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        {transaction.amount < 0 ? (
                          <TrendingDown className="h-5 w-5 text-red-500" />
                        ) : (
                          <TrendingUp className="h-5 w-5 text-green-500" />
                        )}
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {transaction.name}
                        </p>
                        {transaction.merchantName && (
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {transaction.merchantName}
                          </p>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center">
                      {getCategoryIcon(transaction.category)}
                      <span className="ml-2 text-sm text-gray-900 dark:text-white">
                        {transaction.customCategory || transaction.category?.[0] || 'Uncategorized'}
                      </span>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center">
                      <CreditCard className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="text-sm text-gray-900 dark:text-white">
                        {transaction.accountId}
                      </span>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="text-sm text-gray-900 dark:text-white">
                        {new Date(transaction.date).toLocaleDateString()}
                      </span>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <span className={`text-sm font-medium ${getAmountColor(transaction.amount)}`}>
                      {formatAmount(transaction.amount)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {(!transactions || transactions.length === 0) && (
          <div className="text-center py-12">
            <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No Transactions Found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {searchTerm || selectedAccount !== 'all' || selectedCategory !== 'all'
                ? 'Try adjusting your filters to see more transactions.'
                : 'Connect your bank account to start seeing your transactions.'}
            </p>
          </div>
        )}
      </div>

      {/* Summary Stats - Temporarily disabled */}
      {false && (transactions?.length ?? 0) > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-full">
                <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Income</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  ${(transactions
                    ?.filter(t => t.amount > 0)
                    ?.reduce((sum, t) => sum + (t.amount || 0), 0) || 0)
                    .toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-red-100 dark:bg-red-900 rounded-full">
                <TrendingDown className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Expenses</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  ${Math.abs(transactions
                    ?.filter(t => t.amount < 0)
                    ?.reduce((sum, t) => sum + (t.amount || 0), 0) || 0)
                    .toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
                <TrendingUp className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Net Flow</p>
                <p className={`text-2xl font-bold ${getAmountColor(transactions?.reduce((sum, t) => sum + (t.amount || 0), 0) || 0)}`}>
                  {formatAmount(transactions?.reduce((sum, t) => sum + (t.amount || 0), 0) || 0)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 