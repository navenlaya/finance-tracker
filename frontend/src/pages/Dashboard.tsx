import React from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  CreditCard,
  PlusCircle,
  BarChart3,
  AlertCircle,
  Zap
} from 'lucide-react';
import { transactionsApi, plaidApi } from '../services/api';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { PlaidLink } from '../components/PlaidLink';

export const Dashboard: React.FC = () => {
  const queryClient = useQueryClient();
  
  // Fetch dashboard data
  const { data: dashboardData, isLoading: isDashboardLoading } = useQuery(
    'dashboard',
    transactionsApi.getDashboardData
  );

  // Fetch Plaid connection status
  const { data: plaidStatus, isLoading: isPlaidLoading, error: plaidError } = useQuery(
    'plaid-status',
    plaidApi.getConnectionStatus,
    {
      refetchOnWindowFocus: true,
      retry: 3,
      refetchInterval: 5000, // Refetch every 5 seconds
    }
  );

  // Debug logging
  console.log('Dashboard Debug:', {
    plaidStatus,
    plaidLoading: isPlaidLoading,
    plaidError,
    dashboardData,
    isConnected: plaidStatus?.is_connected,
    recentTransactions: dashboardData?.recentTransactions,
    recentTransactionsLength: dashboardData?.recentTransactions?.length,
    shouldShowConnectionAlert: !plaidStatus?.is_connected,
    shouldShowSyncButton: plaidStatus?.is_connected
  });

  if (isDashboardLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Overview of your financial health
          </p>
        </div>

        <div className="flex space-x-3">
          <Button variant="outline" size="md">
            <BarChart3 className="h-4 w-4 mr-2" />
            Export Report
          </Button>
          <Button variant="primary" size="md">
            <PlusCircle className="h-4 w-4 mr-2" />
            Add Transaction
          </Button>
        </div>
      </div>

      {/* Plaid Connection Alert */}
      {(() => {
        const shouldShowConnectionAlert = !plaidStatus?.is_connected;
        console.log('Connection Alert Debug:', {
          plaidStatus,
          isConnected: plaidStatus?.is_connected,
          shouldShowConnectionAlert
        });
        return shouldShowConnectionAlert;
      })() && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mr-3" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                Connect Your Bank Account
              </h3>
              <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                Link your bank account to automatically sync transactions and get AI-powered insights.
              </p>
            </div>
            <PlaidLink variant="outline" size="sm" className="ml-4" />
          </div>
        </div>
      )}

      {/* Sync Transactions Alert for Connected Users - Only show if connected, has accounts, but no recent transactions */}
      {(() => {
        console.log('=== SYNC BUTTON SECTION IS BEING EVALUATED ===');
        const isConnected = plaidStatus?.is_connected;
        const hasAccounts = plaidStatus?.accounts_count && plaidStatus.accounts_count > 0;
        const hasTransactions = dashboardData?.recentTransactions && dashboardData.recentTransactions.length > 0;
        const shouldShowSyncButton = isConnected && hasAccounts && !hasTransactions;
        console.log('Sync Button Debug:', {
          plaidStatus,
          isConnectedField: plaidStatus?.is_connected,
          accountsCount: plaidStatus?.accounts_count,
          recentTransactionsLength: dashboardData?.recentTransactions?.length,
          isConnected,
          hasAccounts,
          hasTransactions,
          shouldShowSyncButton
        });
        return shouldShowSyncButton;
      })() && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-center">
            <Zap className="h-5 w-5 text-blue-600 dark:text-blue-400 mr-3" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                Sync Your Transactions
              </h3>
              <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                Your bank account is connected but transactions need to be synced. Click below to fetch your recent transactions.
              </p>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              className="ml-4"
              onClick={async () => {
                try {
                  console.log('Starting transaction sync...');
                  const result = await plaidApi.syncTransactions(30);
                  console.log('Sync result:', result);
                  alert(`Successfully synced ${result.transactions_synced} transactions!`);
                  // Refresh dashboard data and plaid status
                  queryClient.invalidateQueries('dashboard');
                  queryClient.invalidateQueries('plaid-status');
                } catch (error) {
                  console.error('Error syncing transactions:', error);
                  alert('Failed to sync transactions. Please try again.');
                }
              }}
            >
              <Zap className="h-4 w-4 mr-2" />
              Sync Now
            </Button>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Balance</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ${dashboardData?.totalBalance?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="p-3 bg-primary-100 dark:bg-primary-900 rounded-full">
              <DollarSign className="h-6 w-6 text-primary-600 dark:text-primary-400" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Income</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                +${dashboardData?.monthlyIncome?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900 rounded-full">
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Expenses</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                -${dashboardData?.monthlyExpenses?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="p-3 bg-red-100 dark:bg-red-900 rounded-full">
              <TrendingDown className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Savings</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                ${dashboardData?.monthlySavings?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
              <CreditCard className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts and Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Spending by Category */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Spending by Category
            </h2>
            <Button variant="ghost" size="sm">
              View All
            </Button>
          </div>
          
          {dashboardData?.spendingByCategory?.length ? (
            <div className="space-y-4">
              {dashboardData.spendingByCategory.map((category, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 rounded-full bg-primary-500" />
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {category.category}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      ${category.amount.toLocaleString()}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                      {category.percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                No spending data available. Connect your bank account to see insights.
              </p>
            </div>
          )}
        </div>

        {/* AI Insights */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              AI Insights
            </h2>
            <Zap className="h-5 w-5 text-yellow-500" />
          </div>
          
          <div className="space-y-4">
            <div className="p-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <h3 className="text-sm font-medium text-blue-900 dark:text-blue-200">
                Spending Trend
              </h3>
              <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                Your spending increased by 15% this month compared to last month.
              </p>
            </div>
            
            <div className="p-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <h3 className="text-sm font-medium text-green-900 dark:text-green-200">
                Savings Opportunity
              </h3>
              <p className="text-xs text-green-700 dark:text-green-300 mt-1">
                You could save $200/month by reducing dining out expenses.
              </p>
            </div>
            
            <div className="p-3 bg-gradient-to-r from-purple-50 to-violet-50 dark:from-purple-900/20 dark:to-violet-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
              <h3 className="text-sm font-medium text-purple-900 dark:text-purple-200">
                Budget Alert
              </h3>
              <p className="text-xs text-purple-700 dark:text-purple-300 mt-1">
                You're 80% through your groceries budget for this month.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Recent Transactions
          </h2>
          <Button variant="ghost" size="sm">
            View All
          </Button>
        </div>
        
        {dashboardData?.recentTransactions?.length ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left border-b border-gray-200 dark:border-gray-700">
                  <th className="pb-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="pb-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="pb-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="pb-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider text-right">
                    Amount
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {dashboardData.recentTransactions.slice(0, 5).map((transaction) => (
                  <tr key={transaction.id}>
                    <td className="py-3">
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {transaction.name}
                        </p>
                        {transaction.merchantName && (
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {transaction.merchantName}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="py-3">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                        {transaction.customCategory || transaction.category?.[0] || 'Uncategorized'}
                      </span>
                    </td>
                    <td className="py-3 text-sm text-gray-500 dark:text-gray-400">
                      {new Date(transaction.date).toLocaleDateString()}
                    </td>
                    <td className="py-3 text-right">
                      <span
                        className={`text-sm font-medium ${
                          transaction.transactionType === 'credit'
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-red-600 dark:text-red-400'
                        }`}
                      >
                        {transaction.transactionType === 'credit' ? '+' : '-'}$
                        {transaction.amount.toLocaleString()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">
              No transactions found. Connect your bank account to see your transactions.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}; 