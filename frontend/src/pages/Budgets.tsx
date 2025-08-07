import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Target, 
  Plus, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Edit,
  Trash2
} from 'lucide-react';
import { budgetsApi } from '../services/api';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

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

export const Budgets: React.FC = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingBudget, setEditingBudget] = useState<Budget | null>(null);
  const queryClient = useQueryClient();

  // Fetch budgets data
  const { data: budgets, isLoading } = useQuery(
    'budgets',
    budgetsApi.getBudgets,
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  ) as { data: Budget[] | undefined; isLoading: boolean };

  // Create budget mutation
  const createBudgetMutation = useMutation(
    budgetsApi.createBudget,
    {
      onSuccess: () => {
        queryClient.invalidateQueries('budgets');
        setShowCreateModal(false);
      },
    }
  );

  // Update budget mutation
  const updateBudgetMutation = useMutation(
    budgetsApi.updateBudget,
    {
      onSuccess: () => {
        queryClient.invalidateQueries('budgets');
        setEditingBudget(null);
      },
    }
  );

  // Delete budget mutation
  const deleteBudgetMutation = useMutation(
    budgetsApi.deleteBudget,
    {
      onSuccess: () => {
        queryClient.invalidateQueries('budgets');
      },
    }
  );

  function getBudgetStatusColor(budget: Budget): string {
    if (budget.isOverBudget) return 'text-red-600 dark:text-red-400';
    if (budget.shouldAlert) return 'text-yellow-600 dark:text-yellow-400';
    if (budget.utilizationPercentage > 0.5) return 'text-blue-600 dark:text-blue-400';
    return 'text-green-600 dark:text-green-400';
  }

  function getBudgetStatusIcon(budget: Budget): React.ReactNode {
    if (budget.isOverBudget) return <XCircle className="h-5 w-5 text-red-500" />;
    if (budget.shouldAlert) return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    if (budget.utilizationPercentage > 0.5) return <TrendingUp className="h-5 w-5 text-blue-500" />;
    return <CheckCircle className="h-5 w-5 text-green-500" />;
  }

  function getProgressBarColor(budget: Budget): string {
    if (budget.isOverBudget) return 'bg-red-500';
    if (budget.shouldAlert) return 'bg-yellow-500';
    if (budget.utilizationPercentage > 0.5) return 'bg-blue-500';
    return 'bg-green-500';
  }

  if (isLoading) {
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
            Budgets
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Set spending limits and track your budget progress
          </p>
        </div>

        <Button 
          variant="primary" 
          size="md"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus className="h-4 w-4 mr-2" />
          Create Budget
        </Button>
      </div>

      {/* Budgets Grid */}
      {budgets && budgets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {budgets.map((budget) => (
            <div key={budget.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
                    <Target className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {budget.name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {budget.category}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getBudgetStatusIcon(budget)}
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setEditingBudget(budget)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => {
                      if (confirm('Are you sure you want to delete this budget?')) {
                        deleteBudgetMutation.mutate(budget.id);
                      }
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                {/* Progress Bar */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Progress
                    </span>
                    <span className={`text-sm font-medium ${getBudgetStatusColor(budget)}`}>
                      {budget.utilizationPercentage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getProgressBarColor(budget)}`}
                      style={{ width: `${Math.min(budget.utilizationPercentage * 100, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Amounts */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Spent</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">
                      ${budget.spentAmount.toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Remaining</p>
                    <p className={`text-lg font-bold ${budget.remainingAmount < 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white'}`}>
                      ${budget.remainingAmount.toFixed(2)}
                    </p>
                  </div>
                </div>

                {/* Budget Limit */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Budget Limit</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    ${budget.budgetLimit.toFixed(2)}
                  </span>
                </div>

                {/* Period */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Period</span>
                  <span className="text-sm text-gray-900 dark:text-white capitalize">
                    {budget.periodType}
                  </span>
                </div>

                {/* Status */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Status</span>
                  <span className={`text-sm font-medium ${getBudgetStatusColor(budget)}`}>
                    {budget.isOverBudget ? 'Over Budget' : 
                     budget.shouldAlert ? 'Warning' : 
                     budget.utilizationPercentage > 0.5 ? 'On Track' : 'Good'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No Budgets Created
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Create your first budget to start tracking your spending limits.
          </p>
          <Button 
            variant="primary"
            onClick={() => setShowCreateModal(true)}
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Your First Budget
          </Button>
        </div>
      )}

      {/* Summary Stats */}
      {budgets && budgets.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
                <Target className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Budgets</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {budgets.length}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-full">
                <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">On Track</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {budgets.filter(b => !b.isOverBudget && !b.shouldAlert).length}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-full">
                <AlertTriangle className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Warnings</p>
                <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {budgets.filter(b => b.shouldAlert && !b.isOverBudget).length}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-red-100 dark:bg-red-900 rounded-full">
                <XCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Over Budget</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {budgets.filter(b => b.isOverBudget).length}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create/Edit Budget Modal */}
      {(showCreateModal || editingBudget) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              {editingBudget ? 'Edit Budget' : 'Create Budget'}
            </h2>
            
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const budgetData = {
                name: formData.get('name') as string,
                category: formData.get('category') as string,
                budgetLimit: parseFloat(formData.get('budgetLimit') as string),
                periodType: formData.get('periodType') as string,
                startDate: formData.get('startDate') as string,
                endDate: formData.get('endDate') as string,
                alertThreshold: parseFloat(formData.get('alertThreshold') as string),
                autoRollover: formData.get('autoRollover') === 'on',
              };

              if (editingBudget) {
                updateBudgetMutation.mutate({ id: editingBudget.id, ...budgetData });
              } else {
                createBudgetMutation.mutate(budgetData);
              }
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Budget Name
                  </label>
                  <input
                    type="text"
                    name="name"
                    defaultValue={editingBudget?.name}
                    required
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Category
                  </label>
                  <select
                    name="category"
                    defaultValue={editingBudget?.category}
                    required
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">Select Category</option>
                    <option value="food">Food & Dining</option>
                    <option value="transport">Transportation</option>
                    <option value="shopping">Shopping</option>
                    <option value="entertainment">Entertainment</option>
                    <option value="health">Health & Fitness</option>
                    <option value="utilities">Utilities</option>
                    <option value="housing">Housing</option>
                    <option value="education">Education</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Budget Limit
                  </label>
                  <input
                    type="number"
                    name="budgetLimit"
                    defaultValue={editingBudget?.budgetLimit}
                    min="0"
                    step="0.01"
                    required
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Period Type
                  </label>
                  <select
                    name="periodType"
                    defaultValue={editingBudget?.periodType}
                    required
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="monthly">Monthly</option>
                    <option value="weekly">Weekly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Start Date
                    </label>
                    <input
                      type="date"
                      name="startDate"
                      defaultValue={editingBudget?.startDate}
                      required
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      End Date
                    </label>
                    <input
                      type="date"
                      name="endDate"
                      defaultValue={editingBudget?.endDate}
                      required
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Alert Threshold (%)
                  </label>
                  <input
                    type="number"
                    name="alertThreshold"
                    defaultValue={editingBudget?.alertThreshold || 80}
                    min="0"
                    max="100"
                    step="5"
                    required
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="autoRollover"
                    defaultChecked={editingBudget?.autoRollover}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                    Auto-rollover to next period
                  </label>
                </div>
              </div>

              <div className="flex space-x-3 mt-6">
                <Button
                  type="submit"
                  variant="primary"
                  disabled={createBudgetMutation.isLoading || updateBudgetMutation.isLoading}
                >
                  {createBudgetMutation.isLoading || updateBudgetMutation.isLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    editingBudget ? 'Update Budget' : 'Create Budget'
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCreateModal(false);
                    setEditingBudget(null);
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}; 