import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  PieChart, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Calendar,
  Target,
  Lightbulb,
  BarChart3,
  LineChart,
  Download,
  AlertTriangle
} from 'lucide-react';
import { mlApi, transactionsApi } from '../services/api';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

export const Insights: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<string>('30');

  // Fetch dashboard data for analytics
  const { data: dashboardData, isLoading: isDashboardLoading } = useQuery(
    'dashboard-data',
    transactionsApi.getDashboardData,
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );

  // Fetch AI insights
  const { data: insights, isLoading: isInsightsLoading } = useQuery(
    'insights',
    mlApi.getInsights,
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );

  // Fetch spending forecast
  const { data: forecast, isLoading: isForecastLoading } = useQuery(
    'forecast',
    () => mlApi.getForecast(30),
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );

  if (isDashboardLoading || isInsightsLoading || isForecastLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  function getCategoryColor(category: string): string {
    const colors = {
      food: 'bg-orange-500',
      transport: 'bg-blue-500',
      shopping: 'bg-purple-500',
      entertainment: 'bg-pink-500',
      health: 'bg-green-500',
      utilities: 'bg-yellow-500',
      housing: 'bg-indigo-500',
      education: 'bg-teal-500',
      other: 'bg-gray-500',
    };
    return colors[category as keyof typeof colors] || 'bg-gray-500';
  }

  function detectCategoryFromName(name: string): string {
    const lowerName = name.toLowerCase();
    
    // Food & Dining
    if (lowerName.includes('mcdonald') || lowerName.includes('starbucks') || 
        lowerName.includes('restaurant') || lowerName.includes('cafe') || 
        lowerName.includes('pizza') || lowerName.includes('burger') ||
        lowerName.includes('food') || lowerName.includes('dining') ||
        lowerName.includes('grubhub') || lowerName.includes('doordash') ||
        lowerName.includes('uber eats') || lowerName.includes('postmates')) {
      return 'Food & Dining';
    }
    
    // Transportation
    if (lowerName.includes('uber') || lowerName.includes('lyft') || 
        lowerName.includes('taxi') || lowerName.includes('gas') ||
        lowerName.includes('shell') || lowerName.includes('exxon') ||
        lowerName.includes('chevron') || lowerName.includes('bp') ||
        lowerName.includes('parking') || lowerName.includes('toll') ||
        lowerName.includes('metro') || lowerName.includes('bus') ||
        lowerName.includes('train') || lowerName.includes('airline')) {
      return 'Transportation';
    }
    
    // Shopping
    if (lowerName.includes('amazon') || lowerName.includes('walmart') || 
        lowerName.includes('target') || lowerName.includes('costco') ||
        lowerName.includes('best buy') || lowerName.includes('home depot') ||
        lowerName.includes('lowes') || lowerName.includes('macy') ||
        lowerName.includes('nordstrom') || lowerName.includes('shop')) {
      return 'Shopping';
    }
    
    // Entertainment
    if (lowerName.includes('netflix') || lowerName.includes('spotify') || 
        lowerName.includes('hulu') || lowerName.includes('disney') ||
        lowerName.includes('movie') || lowerName.includes('theater') ||
        lowerName.includes('concert') || lowerName.includes('game') ||
        lowerName.includes('steam') || lowerName.includes('playstation')) {
      return 'Entertainment';
    }
    
    // Health & Fitness
    if (lowerName.includes('gym') || lowerName.includes('fitness') || 
        lowerName.includes('pharmacy') || lowerName.includes('cvs') ||
        lowerName.includes('walgreens') || lowerName.includes('doctor') ||
        lowerName.includes('medical') || lowerName.includes('dental') ||
        lowerName.includes('vision') || lowerName.includes('health')) {
      return 'Health & Fitness';
    }
    
    // Utilities & Bills
    if (lowerName.includes('electric') || lowerName.includes('gas bill') || 
        lowerName.includes('water') || lowerName.includes('internet') ||
        lowerName.includes('phone') || lowerName.includes('cable') ||
        lowerName.includes('at&t') || lowerName.includes('verizon') ||
        lowerName.includes('comcast') || lowerName.includes('spectrum')) {
      return 'Utilities & Bills';
    }
    
    // Banking & Finance
    if (lowerName.includes('bank') || lowerName.includes('atm') || 
        lowerName.includes('credit card') || lowerName.includes('loan') ||
        lowerName.includes('mortgage') || lowerName.includes('insurance')) {
      return 'Banking & Finance';
    }
    
    // Income
    if (lowerName.includes('deposit') || lowerName.includes('salary') || 
        lowerName.includes('payroll') || lowerName.includes('refund') ||
        lowerName.includes('transfer in')) {
      return 'Income';
    }
    
    return 'Other';
  }

  function getCategoryIcon(category: string[] | undefined, transactionName?: string): React.ReactNode {
    // First try to use Plaid categories
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
    } else if (category?.includes('utilities') || category?.includes('bills')) {
      return <span className="text-yellow-500">💡</span>;
    } else if (category?.includes('housing') || category?.includes('rent')) {
      return <span className="text-indigo-500">🏠</span>;
    } else if (category?.includes('education')) {
      return <span className="text-teal-500">📚</span>;
    }
    
    // Fallback to name-based detection
    if (transactionName) {
      const detectedCategory = detectCategoryFromName(transactionName);
      if (detectedCategory === 'Food & Dining') return <span className="text-orange-500">🍽️</span>;
      if (detectedCategory === 'Transportation') return <span className="text-blue-500">🚗</span>;
      if (detectedCategory === 'Shopping') return <span className="text-purple-500">🛍️</span>;
      if (detectedCategory === 'Entertainment') return <span className="text-pink-500">🎬</span>;
      if (detectedCategory === 'Health & Fitness') return <span className="text-green-500">🏥</span>;
      if (detectedCategory === 'Utilities & Bills') return <span className="text-yellow-500">💡</span>;
      if (detectedCategory === 'Banking & Finance') return <span className="text-indigo-500">🏦</span>;
      if (detectedCategory === 'Income') return <span className="text-teal-500">💰</span>;
    }
    
    return <span className="text-gray-500">💰</span>;
  }

  function getInsightIcon(insightType: string): React.ReactNode {
    switch (insightType) {
      case 'trend':
        return <TrendingUp className="h-5 w-5 text-blue-500" />;
      case 'anomaly':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'recommendation':
        return <Lightbulb className="h-5 w-5 text-yellow-500" />;
      default:
        return <Lightbulb className="h-5 w-5 text-gray-500" />;
    }
  }

  function getTrendIcon(trend: string): React.ReactNode {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="h-4 w-4 text-red-500" />;
      case 'decreasing':
        return <TrendingDown className="h-4 w-4 text-green-500" />;
      default:
        return <BarChart3 className="h-4 w-4 text-gray-500" />;
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Insights
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            AI-powered spending analysis and financial insights
          </p>
        </div>

        <div className="flex space-x-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
          <Button variant="outline" size="md">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900 rounded-full">
              <DollarSign className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Balance</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ${dashboardData?.totalBalance?.toLocaleString() || '0'}
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
              <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Income</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                ${dashboardData?.monthlyIncome?.toLocaleString() || '0'}
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
              <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Expenses</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                ${dashboardData?.monthlyExpenses?.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-full">
              <Target className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Savings</p>
              <p className={`text-2xl font-bold ${(dashboardData?.monthlySavings || 0) >= 0 ? 'text-purple-600 dark:text-purple-400' : 'text-red-600 dark:text-red-400'}`}>
                ${Math.abs(dashboardData?.monthlySavings || 0).toLocaleString()}
                {(dashboardData?.monthlySavings || 0) < 0 && ' (Deficit)'}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Spending by Category */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Spending by Category
            </h2>
            <PieChart className="h-5 w-5 text-gray-400" />
          </div>

          <div className="space-y-4">
            {dashboardData?.spendingByCategory && dashboardData.spendingByCategory.length > 0 ? (
              dashboardData.spendingByCategory.map((category) => (
                <div key={category.category} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full ${getCategoryColor(category.category)} mr-3`} />
                    <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                      {category.category}
                    </span>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      ${category.amount.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {category.percentage.toFixed(1)}%
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <PieChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">
                  No spending data available. Connect your bank account to see category breakdowns.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* AI Insights */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              AI Insights
            </h2>
            <Lightbulb className="h-5 w-5 text-gray-400" />
          </div>

          <div className="space-y-4">
            {insights && insights.length > 0 ? (
              insights.slice(0, 5).map((insight, index) => (
                <div key={index} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-start">
                    {getInsightIcon(insight.insightType)}
                    <div className="ml-3 flex-1">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                        {insight.title}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {insight.description}
                      </p>
                      {insight.category && (
                        <span className="inline-block mt-2 px-2 py-1 text-xs bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded">
                          {insight.category}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Lightbulb className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">
                  AI insights will appear here as you add more transactions.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Spending Forecast */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Spending Forecast (Next 30 Days)
          </h2>
          <LineChart className="h-5 w-5 text-gray-400" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {forecast && forecast.length > 0 ? (
            forecast.map((item, index) => (
              <div key={index} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                    {item.category}
                  </span>
                  {getTrendIcon(item.trend)}
                </div>
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  ${item.forecastAmount.toFixed(2)}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Confidence: {item.confidenceIntervalLower.toFixed(0)}% - {item.confidenceIntervalUpper.toFixed(0)}%
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Trend: {item.trend}
                </p>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center py-8">
              <LineChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                Spending forecasts will appear here as we analyze your spending patterns.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Transactions Summary */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Recent Activity
          </h2>
          <Calendar className="h-5 w-5 text-gray-400" />
        </div>

        <div className="space-y-3">
          {dashboardData?.recentTransactions?.slice(0, 5).map((transaction) => {
            // Debug logging
            console.log('Transaction data:', transaction);
            console.log('Category:', transaction.category);
            console.log('Custom Category:', transaction.customCategory);
            
            return (
            <div key={transaction.id} className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-700 last:border-b-0">
              <div className="flex items-center">
                <div className="flex-shrink-0 mr-3">
                  {getCategoryIcon(transaction.category, transaction.name)}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {transaction.name}
                  </p>
                  <div className="flex items-center mt-1">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(transaction.date).toLocaleDateString()}
                    </span>
                    <span className="mx-2 text-gray-300">•</span>
                    <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                      {transaction.customCategory || transaction.category?.[0] || detectCategoryFromName(transaction.name)}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-sm font-medium ${transaction.amount > 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
                  {transaction.amount > 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                </p>
                <div className="flex items-center justify-end mt-1">
                  <div className={`w-2 h-2 rounded-full ${transaction.amount > 0 ? 'bg-red-500' : 'bg-green-500'} mr-2`} />
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {transaction.amount > 0 ? 'Expense' : 'Income'}
                  </span>
                </div>
              </div>
            </div>
          );
          })}
        </div>
      </div>

      {/* Savings Rate Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Savings Rate
          </h3>
          <div className="text-center">
            <div className={`text-3xl font-bold ${(dashboardData?.monthlySavings || 0) >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'} mb-2`}>
              {dashboardData?.monthlyIncome && dashboardData.monthlyIncome > 0
                ? Math.abs((dashboardData.monthlySavings / dashboardData.monthlyIncome) * 100).toFixed(1)
                : '0'}%
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              of your income is being saved
            </p>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Spending Efficiency
          </h3>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">
              {dashboardData?.monthlyIncome && dashboardData.monthlyIncome > 0
                ? Math.min((dashboardData.monthlyExpenses / dashboardData.monthlyIncome) * 100, 100).toFixed(1)
                : '0'}%
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              of your income goes to expenses
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}; 