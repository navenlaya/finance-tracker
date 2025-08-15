import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  Brain, 
  Target,
  Lightbulb,
  BarChart3,
  LineChart,
  AlertTriangle,
  Heart,
  Award,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Minus
} from 'lucide-react';
import { mlApi } from '../services/api';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

export const AIInsights: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<string>('30');

  // Fetch AI insights
  const { data: insights, isLoading: isInsightsLoading } = useQuery(
    'ai-insights',
    mlApi.getInsights,
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );

  // Fetch spending forecast
  const { data: forecast, isLoading: isForecastLoading } = useQuery(
    'ai-forecast',
    () => mlApi.getForecast(parseInt(selectedPeriod)),
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );

  // Fetch financial health score
  const { data: healthScore, isLoading: isHealthLoading } = useQuery(
    'ai-health-score',
    mlApi.getHealthScore,
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );

  // Fetch forecast accuracy
  const { data: accuracy, isLoading: isAccuracyLoading } = useQuery(
    'ai-accuracy',
    mlApi.getForecastAccuracy,
    {
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );

  if (isInsightsLoading || isForecastLoading || isHealthLoading || isAccuracyLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  function getInsightIcon(insightType: string) {
    switch (insightType) {
      case 'trend':
        return <TrendingUpIcon className="h-5 w-5 text-blue-500" />;
      case 'anomaly':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'recommendation':
        return <Lightbulb className="h-5 w-5 text-yellow-500" />;
      case 'pattern':
        return <BarChart3 className="h-5 w-5 text-purple-500" />;
      case 'alert':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'positive':
        return <Award className="h-5 w-5 text-green-500" />;
      default:
        return <Lightbulb className="h-5 w-5 text-gray-500" />;
    }
  }

  function getTrendIcon(trend: string) {
    switch (trend) {
      case 'increasing':
        return <TrendingUpIcon className="h-4 w-4 text-red-500" />;
      case 'decreasing':
        return <TrendingDownIcon className="h-4 w-4 text-green-500" />;
      case 'stable':
        return <Minus className="h-4 w-4 text-gray-500" />;
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  }

  function getHealthGradeColor(grade: string): string {
    if (grade.startsWith('A')) return 'text-green-600 dark:text-green-400';
    if (grade.startsWith('B')) return 'text-blue-600 dark:text-blue-400';
    if (grade.startsWith('C')) return 'text-yellow-600 dark:text-yellow-400';
    if (grade.startsWith('D')) return 'text-orange-600 dark:text-orange-400';
    return 'text-red-600 dark:text-red-400';
  }

  function getMetricStatusColor(status: string): string {
    switch (status) {
      case 'excellent':
      case 'very_good':
        return 'text-green-600 dark:text-green-400';
      case 'good':
        return 'text-blue-600 dark:text-blue-400';
      case 'fair':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'concerning':
      case 'inadequate':
        return 'text-orange-600 dark:text-orange-400';
      case 'critical':
      case 'negative':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          AI-Powered Financial Insights
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Discover personalized financial analysis, predictions, and recommendations powered by artificial intelligence.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Financial Health Score */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Financial Health Score
            </h2>
            <Heart className="h-6 w-6 text-red-500" />
          </div>

          {healthScore ? (
            <div className="space-y-6">
              {/* Overall Score */}
              <div className="text-center">
                <div className={`text-6xl font-bold ${getHealthGradeColor(healthScore.healthGrade)} mb-2`}>
                  {healthScore.overallScore}
                </div>
                <div className={`text-2xl font-semibold ${getHealthGradeColor(healthScore.healthGrade)}`}>
                  {healthScore.healthGrade}
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                  Overall Financial Health
                </p>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className={`text-lg font-semibold ${getMetricStatusColor(healthScore.metrics.incomeExpenseRatio.status)}`}>
                    {healthScore.metrics.incomeExpenseRatio.score}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Income/Expense Ratio
                  </div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className={`text-lg font-semibold ${getMetricStatusColor(healthScore.metrics.savingsRate.status)}`}>
                    {healthScore.metrics.savingsRate.score}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Savings Rate
                  </div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className={`text-lg font-semibold ${getMetricStatusColor(healthScore.metrics.spendingConsistency.status)}`}>
                    {healthScore.metrics.spendingConsistency.score}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Consistency
                  </div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className={`text-lg font-semibold ${getMetricStatusColor(healthScore.metrics.emergencyFundScore.status)}`}>
                    {healthScore.metrics.emergencyFundScore.score}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Emergency Fund
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                  Recommendations
                </h3>
                <div className="space-y-2">
                  {healthScore.recommendations.map((rec, index) => (
                    <div key={index} className="text-sm text-gray-600 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                      {rec}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Heart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                No health score data available.
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
            <Brain className="h-6 w-6 text-purple-500" />
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
                        <span className="inline-block mt-2 px-2 py-1 text-xs bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded">
                          {insight.category}
                        </span>
                      )}
                      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        Confidence: {(insight.confidenceScore * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">
                  AI insights will appear here as you add more transactions.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Spending Forecast */}
      <div className="card mt-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Spending Forecast
          </h2>
          <div className="flex items-center space-x-4">
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="7">7 days</option>
              <option value="30">30 days</option>
              <option value="90">90 days</option>
            </select>
            <LineChart className="h-6 w-6 text-blue-500" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {forecast && forecast.length > 0 ? (
            forecast.map((item, index) => (
              <div key={index} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {item.category}
                  </h3>
                  {getTrendIcon(item.trend)}
                </div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  ${item.forecastAmount.toFixed(2)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  Confidence: ${item.confidenceIntervalLower.toFixed(2)} - ${item.confidenceIntervalUpper.toFixed(2)}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                  Trend: {item.trend}
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center py-8">
              <LineChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                No forecast data available.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Forecast Accuracy */}
      {accuracy && (
        <div className="card mt-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Forecast Accuracy
            </h2>
            <Target className="h-6 w-6 text-green-500" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400 mb-2">
                {(accuracy.overallAccuracy * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Overall Accuracy
              </div>
            </div>
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                {(accuracy.categoryAccuracy * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Category Accuracy
              </div>
            </div>
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400 mb-2">
                {(accuracy.trendAccuracy * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Trend Accuracy
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
