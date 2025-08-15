"""
AI-powered spending forecasting service.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
import numpy as np
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import ForecastData

logger = logging.getLogger(__name__)


class SpendingForecastService:
    """Service for generating spending forecasts using ML techniques."""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def generate_forecast(self, days_ahead: int = 30) -> List[ForecastData]:
        """Generate spending forecast for the specified number of days ahead."""
        try:
            # Get historical transaction data
            transactions = await self._get_historical_transactions()
            if not transactions:
                return self._get_default_forecast(days_ahead)
            
            # Generate forecasts for different categories
            forecasts = []
            
            # Get unique categories
            categories = await self._get_transaction_categories(transactions)
            
            for category in categories:
                category_forecast = await self._forecast_category(
                    transactions, category, days_ahead
                )
                if category_forecast:
                    forecasts.append(category_forecast)
            
            # Add overall spending forecast
            overall_forecast = await self._forecast_overall_spending(
                transactions, days_ahead
            )
            if overall_forecast:
                forecasts.append(overall_forecast)
            
            return forecasts
            
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return self._get_default_forecast(days_ahead)
    
    async def _get_historical_transactions(self) -> List[Transaction]:
        """Get historical transactions for forecasting."""
        # Get transactions from the last 6 months for better pattern recognition
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        query = select(Transaction).where(
            and_(
                Transaction.user_id == self.user.id,
                Transaction.date >= six_months_ago
            )
        ).order_by(Transaction.date.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def _get_transaction_categories(self, transactions: List[Transaction]) -> List[str]:
        """Get unique transaction categories."""
        categories = set()
        for txn in transactions:
            if txn.transaction_type == "debit":  # Only forecast expenses
                category = txn.custom_category or (txn.category[0] if txn.category else "Other")
                categories.add(category)
        
        # Return top categories by spending volume
        category_totals = {}
        for txn in transactions:
            if txn.transaction_type == "debit":
                category = txn.custom_category or (txn.category[0] if txn.category else "Other")
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += abs(float(txn.amount))
        
        # Sort by total spending and return top 5 categories
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        return [cat for cat, _ in sorted_categories[:5]]
    
    async def _forecast_category(
        self, 
        transactions: List[Transaction], 
        category: str, 
        days_ahead: int
    ) -> Optional[ForecastData]:
        """Forecast spending for a specific category."""
        try:
            # Filter transactions for this category
            category_transactions = [
                txn for txn in transactions
                if txn.transaction_type == "debit" and
                (txn.custom_category or (txn.category[0] if txn.category else "Other")) == category
            ]
            
            if len(category_transactions) < 5:
                return None
            
            # Group by month for trend analysis
            monthly_data = {}
            for txn in category_transactions:
                month_key = txn.date.replace(day=1)
                if month_key not in monthly_data:
                    monthly_data[month_key] = 0
                monthly_data[month_key] += abs(float(txn.amount))
            
            if len(monthly_data) < 2:
                return None
            
            # Calculate trend and forecast
            months = sorted(monthly_data.keys())
            amounts = [monthly_data[month] for month in months]
            
            # Simple linear regression for trend
            x = np.arange(len(months))
            y = np.array(amounts)
            
            if len(y) > 1:
                # Calculate trend
                slope = np.polyfit(x, y, 1)[0]
                
                # Forecast next month
                next_month_amount = amounts[-1] + slope
                
                # Calculate confidence interval (simplified)
                std_dev = np.std(amounts)
                confidence_lower = max(0, next_month_amount - std_dev)
                confidence_upper = next_month_amount + std_dev
                
                # Determine trend direction
                if slope > 0.1:
                    trend = "increasing"
                elif slope < -0.1:
                    trend = "decreasing"
                else:
                    trend = "stable"
                
                # Scale to daily forecast
                daily_forecast = next_month_amount / 30
                forecast_amount = daily_forecast * days_ahead
                
                return ForecastData(
                    category=category,
                    forecast_amount=Decimal(str(forecast_amount)),
                    confidence_interval_lower=Decimal(str(confidence_lower)),
                    confidence_interval_upper=Decimal(str(confidence_upper)),
                    forecast_date=date.today() + timedelta(days=days_ahead),
                    trend=trend
                )
            
        except Exception as e:
            logger.error(f"Error forecasting category {category}: {e}")
        
        return None
    
    async def _forecast_overall_spending(
        self, 
        transactions: List[Transaction], 
        days_ahead: int
    ) -> Optional[ForecastData]:
        """Forecast overall spending across all categories."""
        try:
            # Group expenses by month
            monthly_expenses = {}
            for txn in transactions:
                if txn.transaction_type == "debit":
                    month_key = txn.date.replace(day=1)
                    if month_key not in monthly_expenses:
                        monthly_expenses[month_key] = 0
                    monthly_expenses[month_key] += abs(float(txn.amount))
            
            if len(monthly_expenses) < 2:
                return None
            
            # Calculate trend
            months = sorted(monthly_expenses.keys())
            amounts = [monthly_expenses[month] for month in months]
            
            x = np.arange(len(months))
            y = np.array(amounts)
            
            if len(y) > 1:
                slope = np.polyfit(x, y, 1)[0]
                
                # Forecast next month
                next_month_amount = amounts[-1] + slope
                
                # Confidence interval
                std_dev = np.std(amounts)
                confidence_lower = max(0, next_month_amount - std_dev)
                confidence_upper = next_month_amount + std_dev
                
                # Trend direction
                if slope > 0.1:
                    trend = "increasing"
                elif slope < -0.1:
                    trend = "decreasing"
                else:
                    trend = "stable"
                
                # Scale to daily forecast
                daily_forecast = next_month_amount / 30
                forecast_amount = daily_forecast * days_ahead
                
                return ForecastData(
                    category="Overall Spending",
                    forecast_amount=Decimal(str(forecast_amount)),
                    confidence_interval_lower=Decimal(str(confidence_lower)),
                    confidence_interval_upper=Decimal(str(confidence_upper)),
                    forecast_date=date.today() + timedelta(days=days_ahead),
                    trend=trend
                )
            
        except Exception as e:
            logger.error(f"Error forecasting overall spending: {e}")
        
        return None
    
    def _get_default_forecast(self, days_ahead: int) -> List[ForecastData]:
        """Return default forecast when no data is available."""
        return [
            ForecastData(
                category="General Expenses",
                forecast_amount=Decimal("500.00"),
                confidence_interval_lower=Decimal("300.00"),
                confidence_interval_upper=Decimal("700.00"),
                forecast_date=date.today() + timedelta(days=days_ahead),
                trend="stable"
            )
        ]
    
    async def get_forecast_accuracy(self) -> Dict[str, float]:
        """Calculate forecast accuracy based on historical predictions."""
        # This would compare previous forecasts with actual spending
        # For now, return a placeholder
        return {
            "overall_accuracy": 0.75,
            "category_accuracy": 0.70,
            "trend_accuracy": 0.80
        }
