"""
AI-powered spending insights and analysis service.
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
from app.schemas.transaction import SpendingInsight

logger = logging.getLogger(__name__)


class SpendingInsightsService:
    """Service for generating AI-powered spending insights."""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def generate_insights(self) -> List[SpendingInsight]:
        """Generate comprehensive spending insights for the user."""
        try:
            insights = []
            
            # Get transaction data for analysis
            transactions = await self._get_user_transactions()
            if not transactions:
                return self._get_default_insights()
            
            # Generate different types of insights
            insights.extend(await self._analyze_spending_trends(transactions))
            insights.extend(await self._detect_spending_anomalies(transactions))
            insights.extend(await self._generate_savings_recommendations(transactions))
            insights.extend(await self._analyze_category_patterns(transactions))
            insights.extend(await self._detect_budget_issues(transactions))
            
            # Sort by confidence score and return top insights
            insights.sort(key=lambda x: x.confidence_score, reverse=True)
            return insights[:10]  # Return top 10 insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return self._get_default_insights()
    
    async def _get_user_transactions(self) -> List[Transaction]:
        """Get user's transactions for analysis."""
        query = select(Transaction).where(
            Transaction.user_id == self.user.id
        ).order_by(Transaction.date.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def _analyze_spending_trends(self, transactions: List[Transaction]) -> List[SpendingInsight]:
        """Analyze spending trends over time."""
        insights = []
        
        if len(transactions) < 10:
            return insights
        
        # Group transactions by month
        monthly_data = {}
        for txn in transactions:
            month_key = txn.date.replace(day=1)
            if month_key not in monthly_data:
                monthly_data[month_key] = {"income": 0, "expenses": 0}
            
            if txn.transaction_type == "credit":
                monthly_data[month_key]["income"] += abs(float(txn.amount))
            else:
                monthly_data[month_key]["expenses"] += abs(float(txn.amount))
        
        if len(monthly_data) < 2:
            return insights
        
        # Calculate month-over-month changes
        months = sorted(monthly_data.keys())
        current_month = months[-1]
        previous_month = months[-2]
        
        current_expenses = monthly_data[current_month]["expenses"]
        previous_expenses = monthly_data[previous_month]["expenses"]
        
        if previous_expenses > 0:
            change_percentage = ((current_expenses - previous_expenses) / previous_expenses) * 100
            
            if change_percentage > 20:
                insights.append(SpendingInsight(
                    insight_type="trend",
                    title="Spending Increase Alert",
                    description=f"Your spending increased by {change_percentage:.1f}% this month compared to last month. Consider reviewing your budget.",
                    confidence_score=0.85,
                    created_at=datetime.utcnow()
                ))
            elif change_percentage < -20:
                insights.append(SpendingInsight(
                    insight_type="trend",
                    title="Great Spending Control",
                    description=f"Your spending decreased by {abs(change_percentage):.1f}% this month! Keep up the good work.",
                    confidence_score=0.80,
                    created_at=datetime.utcnow()
                ))
        
        return insights
    
    async def _detect_spending_anomalies(self, transactions: List[Transaction]) -> List[SpendingInsight]:
        """Detect unusual spending patterns."""
        insights = []
        
        if len(transactions) < 20:
            return insights
        
        # Calculate average daily spending
        daily_spending = {}
        for txn in transactions:
            if txn.transaction_type == "debit":  # Only expenses
                day_key = txn.date
                if day_key not in daily_spending:
                    daily_spending[day_key] = 0
                daily_spending[day_key] += abs(float(txn.amount))
        
        if not daily_spending:
            return insights
        
        # Calculate statistics
        amounts = list(daily_spending.values())
        mean_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        
        if std_amount > 0:
            # Find days with spending > 2 standard deviations from mean
            for day, amount in daily_spending.items():
                z_score = abs((amount - mean_amount) / std_amount)
                if z_score > 2:
                    insights.append(SpendingInsight(
                        insight_type="anomaly",
                        title="Unusual Spending Day",
                        description=f"On {day.strftime('%B %d')}, you spent ${amount:.2f}, which is significantly higher than your average daily spending of ${mean_amount:.2f}.",
                        confidence_score=0.90,
                        created_at=datetime.utcnow()
                    ))
        
        return insights
    
    async def _generate_savings_recommendations(self, transactions: List[Transaction]) -> List[SpendingInsight]:
        """Generate savings recommendations based on spending patterns."""
        insights = []
        
        # Analyze category spending for savings opportunities
        category_spending = {}
        for txn in transactions:
            if txn.transaction_type == "debit":  # Only expenses
                category = txn.custom_category or (txn.category[0] if txn.category else "Other")
                if category not in category_spending:
                    category_spending[category] = 0
                category_spending[category] += abs(float(txn.amount))
        
        if not category_spending:
            return insights
        
        # Find highest spending categories
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
        
        # Generate recommendations for top spending categories
        for category, amount in sorted_categories[:3]:
            if amount > 100:  # Only suggest for significant spending
                potential_savings = amount * 0.2  # Suggest 20% reduction
                insights.append(SpendingInsight(
                    insight_type="recommendation",
                    title=f"Save on {category.title()}",
                    description=f"You spent ${amount:.2f} on {category.lower()} this month. Consider reducing this by 20% to save ${potential_savings:.2f} monthly.",
                    category=category,
                    confidence_score=0.75,
                    created_at=datetime.utcnow()
                ))
        
        return insights
    
    async def _analyze_category_patterns(self, transactions: List[Transaction]) -> List[SpendingInsight]:
        """Analyze spending patterns by category."""
        insights = []
        
        # Group transactions by category and day of week
        category_day_patterns = {}
        for txn in transactions:
            if txn.transaction_type == "debit":  # Only expenses
                category = txn.custom_category or (txn.category[0] if txn.category else "Other")
                day_of_week = txn.date.strftime("%A")
                
                if category not in category_day_patterns:
                    category_day_patterns[category] = {}
                if day_of_week not in category_day_patterns[category]:
                    category_day_patterns[category][day_of_week] = 0
                
                category_day_patterns[category][day_of_week] += abs(float(txn.amount))
        
        # Find patterns
        for category, day_data in category_day_patterns.items():
            if len(day_data) >= 3:  # Need at least 3 days of data
                max_day = max(day_data.items(), key=lambda x: x[1])
                min_day = min(day_data.items(), key=lambda x: x[1])
                
                if max_day[1] > min_day[1] * 2:  # Significant difference
                    insights.append(SpendingInsight(
                        insight_type="pattern",
                        title=f"{category.title()} Spending Pattern",
                        description=f"You tend to spend more on {category.lower()} on {max_day[0]}s (${max_day[1]:.2f}) compared to {min_day[0]}s (${min_day[1]:.2f}).",
                        category=category,
                        confidence_score=0.70,
                        created_at=datetime.utcnow()
                    ))
        
        return insights
    
    async def _detect_budget_issues(self, transactions: List[Transaction]) -> List[SpendingInsight]:
        """Detect potential budget issues."""
        insights = []
        
        # This would integrate with actual budget data
        # For now, provide general financial health insights
        
        # Calculate monthly income vs expenses
        current_month = datetime.utcnow().replace(day=1)
        monthly_income = 0
        monthly_expenses = 0
        
        for txn in transactions:
            if txn.date >= current_month:
                if txn.transaction_type == "credit":
                    monthly_income += abs(float(txn.amount))
                else:
                    monthly_expenses += abs(float(txn.amount))
        
        if monthly_income > 0:
            expense_ratio = monthly_expenses / monthly_income
            
            if expense_ratio > 0.9:
                insights.append(SpendingInsight(
                    insight_type="alert",
                    title="High Expense Ratio",
                    description=f"Your expenses are {expense_ratio:.1%} of your income this month. Consider reducing spending to improve savings.",
                    confidence_score=0.85,
                    created_at=datetime.utcnow()
                ))
            elif expense_ratio < 0.5:
                insights.append(SpendingInsight(
                    insight_type="positive",
                    title="Excellent Savings Rate",
                    description=f"Great job! You're only spending {expense_ratio:.1%} of your income, leaving plenty for savings and investments.",
                    confidence_score=0.80,
                    created_at=datetime.utcnow()
                ))
        
        return insights
    
    def _get_default_insights(self) -> List[SpendingInsight]:
        """Return default insights when no transaction data is available."""
        return [
            SpendingInsight(
                insight_type="info",
                title="Welcome to Finance Tracker!",
                description="Start connecting your bank accounts and adding transactions to receive personalized AI insights.",
                confidence_score=1.0,
                created_at=datetime.utcnow()
            )
        ]
