import React from 'react';
import { useQuery } from 'react-query';
import { 
  CreditCard, 
  DollarSign, 
  TrendingUp, 
  RefreshCw,
  Plus,
  Settings
} from 'lucide-react';
import { accountsApi, plaidApi } from '../services/api';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { PlaidLink } from '../components/PlaidLink';

export const Accounts: React.FC = () => {
  // Fetch accounts data
  const { data: accounts, isLoading: isAccountsLoading, refetch: refetchAccounts } = useQuery(
    'accounts',
    accountsApi.getAccounts,
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );

  // Fetch Plaid connection status
  const { data: plaidStatus, isLoading: isPlaidLoading } = useQuery(
    'plaid-status',
    plaidApi.getConnectionStatus,
    {
      refetchOnWindowFocus: true,
      retry: 3,
    }
  );

  const isConnected = plaidStatus?.isConnected || plaidStatus?.is_connected;
  const hasAccounts = accounts && accounts.length > 0;

  if (isAccountsLoading || isPlaidLoading) {
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
            Accounts
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage your connected bank accounts
          </p>
        </div>

        <div className="flex space-x-3">
          {isConnected && hasAccounts && (
            <Button 
              variant="outline" 
              size="md"
              onClick={async () => {
                try {
                  await plaidApi.syncAccounts();
                  refetchAccounts();
                } catch (error) {
                  console.error('Error syncing accounts:', error);
                }
              }}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Sync Accounts
            </Button>
          )}
          <PlaidLink variant="primary" size="md">
            <Plus className="h-4 w-4 mr-2" />
            Add Account
          </PlaidLink>
        </div>
      </div>

      {/* Connection Alert */}
      {!isConnected && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div className="flex items-center">
            <CreditCard className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mr-3" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                No Bank Accounts Connected
              </h3>
              <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                Connect your bank account to start tracking your finances automatically.
              </p>
            </div>
            <PlaidLink variant="outline" size="sm" className="ml-4" />
          </div>
        </div>
      )}

      {/* Accounts Grid */}
      {hasAccounts ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {accounts.map((account) => (
            <div key={account.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
                    <CreditCard className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {account.accountName}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {account.institutionName} • {account.accountType}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  <Settings className="h-4 w-4" />
                </Button>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Current Balance</span>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    ${account.currentBalance?.toLocaleString() || '0.00'}
                  </span>
                </div>

                {account.availableBalance && account.availableBalance !== account.currentBalance && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Available Balance</span>
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      ${account.availableBalance.toLocaleString()}
                    </span>
                  </div>
                )}

                {account.mask && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Account Number</span>
                    <span className="text-sm font-mono text-gray-700 dark:text-gray-300">
                      ****{account.mask}
                    </span>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500 dark:text-gray-400">Last Updated</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date().toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : isConnected ? (
        <div className="text-center py-12">
          <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No Accounts Found
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Your bank account is connected but no accounts were found. Try syncing your accounts.
          </p>
          <Button 
            variant="outline"
            onClick={async () => {
              try {
                await plaidApi.syncAccounts();
                refetchAccounts();
              } catch (error) {
                console.error('Error syncing accounts:', error);
              }
            }}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Sync Accounts
          </Button>
        </div>
      ) : null}

      {/* Summary Stats */}
      {hasAccounts && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-full">
                <DollarSign className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Balance</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  ${accounts?.reduce((sum, account) => sum + (account.currentBalance || 0), 0).toLocaleString() || '0'}
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
                <p className="text-sm text-gray-600 dark:text-gray-400">Accounts</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {accounts?.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-full">
                <CreditCard className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Institutions</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {new Set(accounts?.map(account => account.institutionName)).size || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 