"""
Financial health scoring and analysis service.
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Tuple
from decimal import Decimal
import numpy as np
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction
from app.models.user import User

logger = logging.getLogger(__name__)


class FinancialHealthService:
    """Service for calculating financial health scores and metrics."""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def calculate_health_score(self) -> Dict[str, Any]:
        """Calculate comprehensive financial health score."""
        try:
            # Get transaction data
            transactions = await self._get_user_transactions()
            if not transactions:
                return self._get_default_health_score()
            
            # Calculate various health metrics
            income_expense_ratio = await self._calculate_income_expense_ratio(transactions)
            savings_rate = await self._calculate_savings_rate(transactions)
            spending_consistency = await self._calculate_spending_consistency(transactions)
            emergency_fund_score = await self._calculate_emergency_fund_score(transactions)
            debt_management = await self._calculate_debt_management_score(transactions)
            category_diversity = await self._calculate_category_diversity(transactions)
            
            # Calculate overall health score (weighted average)
            overall_score = self._calculate_overall_score({
                'income_expense_ratio': income_expense_ratio,
                'savings_rate': savings_rate,
                'spending_consistency': spending_consistency,
                'emergency_fund_score': emergency_fund_score,
                'debt_management': debt_management,
                'category_diversity': category_diversity
            })
            
            # Generate health grade
            health_grade = self._get_health_grade(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations({
                'income_expense_ratio': income_expense_ratio,
                'savings_rate': savings_rate,
                'spending_consistency': spending_consistency,
                'emergency_fund_score': emergency_fund_score,
                'debt_management': debt_management,
                'category_diversity': category_diversity
            })
            
            return {
                'overall_score': overall_score,
                'health_grade': health_grade,
                'metrics': {
                    'income_expense_ratio': income_expense_ratio,
                    'savings_rate': savings_rate,
                    'spending_consistency': spending_consistency,
                    'emergency_fund_score': emergency_fund_score,
                    'debt_management': debt_management,
                    'category_diversity': category_diversity
                },
                'recommendations': recommendations,
                'calculated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return self._get_default_health_score()
    
    async def _get_user_transactions(self) -> List[Transaction]:
        """Get user's transactions for analysis."""
        # Get transactions from the last 12 months
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        
        query = select(Transaction).where(
            and_(
                Transaction.user_id == self.user.id,
                Transaction.date >= one_year_ago
            )
        ).order_by(Transaction.date.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def _calculate_income_expense_ratio(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Calculate income to expense ratio."""
        monthly_data = {}
        
        for txn in transactions:
            month_key = txn.date.replace(day=1)
            if month_key not in monthly_data:
                monthly_data[month_key] = {"income": 0, "expenses": 0}
            
            if txn.transaction_type == "credit":
                monthly_data[month_key]["income"] += abs(float(txn.amount))
            else:
                monthly_data[month_key]["expenses"] += abs(float(txn.amount))
        
        if not monthly_data:
            return {"score": 0, "ratio": 0, "status": "insufficient_data"}
        
        # Calculate average monthly ratio
        total_income = sum(data["income"] for data in monthly_data.values())
        total_expenses = sum(data["expenses"] for data in monthly_data.values())
        
        if total_income == 0:
            return {"score": 0, "ratio": 0, "status": "no_income"}
        
        ratio = total_expenses / total_income
        
        # Score based on ratio (lower is better)
        if ratio <= 0.5:
            score = 100
            status = "excellent"
        elif ratio <= 0.7:
            score = 80
            status = "good"
        elif ratio <= 0.9:
            score = 60
            status = "fair"
        elif ratio <= 1.1:
            score = 40
            status = "concerning"
        else:
            score = 20
            status = "critical"
        
        return {
            "score": score,
            "ratio": ratio,
            "status": status,
            "monthly_income": total_income / len(monthly_data),
            "monthly_expenses": total_expenses / len(monthly_data)
        }
    
    async def _calculate_savings_rate(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Calculate savings rate."""
        monthly_data = {}
        
        for txn in transactions:
            month_key = txn.date.replace(day=1)
            if month_key not in monthly_data:
                monthly_data[month_key] = {"income": 0, "expenses": 0}
            
            if txn.transaction_type == "credit":
                monthly_data[month_key]["income"] += abs(float(txn.amount))
            else:
                monthly_data[month_key]["expenses"] += abs(float(txn.amount))
        
        if not monthly_data:
            return {"score": 0, "rate": 0, "status": "insufficient_data"}
        
        # Calculate average monthly savings rate
        total_income = sum(data["income"] for data in monthly_data.values())
        total_expenses = sum(data["expenses"] for data in monthly_data.values())
        
        if total_income == 0:
            return {"score": 0, "rate": 0, "status": "no_income"}
        
        savings_rate = (total_income - total_expenses) / total_income
        
        # Score based on savings rate (higher is better)
        if savings_rate >= 0.3:
            score = 100
            status = "excellent"
        elif savings_rate >= 0.2:
            score = 85
            status = "very_good"
        elif savings_rate >= 0.1:
            score = 70
            status = "good"
        elif savings_rate >= 0:
            score = 50
            status = "fair"
        else:
            score = 20
            status = "negative"
        
        return {
            "score": score,
            "rate": savings_rate,
            "status": status,
            "monthly_savings": (total_income - total_expenses) / len(monthly_data)
        }
    
    async def _calculate_spending_consistency(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Calculate spending consistency score."""
        # Group expenses by month
        monthly_expenses = {}
        for txn in transactions:
            if txn.transaction_type == "debit":
                month_key = txn.date.replace(day=1)
                if month_key not in monthly_expenses:
                    monthly_expenses[month_key] = 0
                monthly_expenses[month_key] += abs(float(txn.amount))
        
        if len(monthly_expenses) < 3:
            return {"score": 50, "consistency": 0, "status": "insufficient_data"}
        
        # Calculate coefficient of variation (lower is more consistent)
        amounts = list(monthly_expenses.values())
        mean_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        
        if mean_amount == 0:
            return {"score": 50, "consistency": 0, "status": "no_expenses"}
        
        cv = std_amount / mean_amount
        
        # Score based on consistency (lower CV is better)
        if cv <= 0.2:
            score = 100
            status = "very_consistent"
        elif cv <= 0.4:
            score = 80
            status = "consistent"
        elif cv <= 0.6:
            score = 60
            status = "moderate"
        elif cv <= 0.8:
            score = 40
            status = "inconsistent"
        else:
            score = 20
            status = "highly_inconsistent"
        
        return {
            "score": score,
            "consistency": 1 - min(cv, 1),  # Convert to consistency score
            "status": status,
            "coefficient_of_variation": cv
        }
    
    async def _calculate_emergency_fund_score(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Calculate emergency fund adequacy score."""
        # This is a simplified calculation
        # In a real app, you'd need account balance data
        
        # For now, estimate based on monthly expenses
        monthly_expenses = await self._get_monthly_expenses(transactions)
        
        if monthly_expenses == 0:
            return {"score": 50, "months_covered": 0, "status": "insufficient_data"}
        
        # Assume emergency fund should cover 3-6 months of expenses
        # This is a placeholder - would need actual account balance data
        emergency_fund_months = 3  # Placeholder
        
        if emergency_fund_months >= 6:
            score = 100
            status = "excellent"
        elif emergency_fund_months >= 4:
            score = 80
            status = "good"
        elif emergency_fund_months >= 3:
            score = 60
            status = "adequate"
        elif emergency_fund_months >= 2:
            score = 40
            status = "inadequate"
        else:
            score = 20
            status = "critical"
        
        return {
            "score": score,
            "months_covered": emergency_fund_months,
            "status": status,
            "recommended_months": 6
        }
    
    async def _calculate_debt_management_score(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Calculate debt management score."""
        # This would require actual debt account data
        # For now, return a placeholder score
        return {
            "score": 70,
            "status": "good",
            "note": "Requires debt account integration"
        }
    
    async def _calculate_category_diversity(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Calculate spending category diversity score."""
        category_counts = {}
        
        for txn in transactions:
            if txn.transaction_type == "debit":
                category = txn.custom_category or (txn.category[0] if txn.category else "Other")
                if category not in category_counts:
                    category_counts[category] = 0
                category_counts[category] += 1
        
        if not category_counts:
            return {"score": 0, "diversity": 0, "status": "no_expenses"}
        
        # Calculate diversity using Shannon entropy
        total_transactions = sum(category_counts.values())
        if total_transactions == 0:
            return {"score": 0, "diversity": 0, "status": "no_expenses"}
        
        entropy = 0
        for count in category_counts.values():
            p = count / total_transactions
            if p > 0:
                entropy -= p * np.log2(p)
        
        # Normalize entropy (0 to 1)
        max_entropy = np.log2(len(category_counts))
        if max_entropy == 0:
            normalized_entropy = 0
        else:
            normalized_entropy = entropy / max_entropy
        
        # Score based on diversity
        if normalized_entropy >= 0.8:
            score = 100
            status = "excellent"
        elif normalized_entropy >= 0.6:
            score = 80
            status = "good"
        elif normalized_entropy >= 0.4:
            score = 60
            status = "moderate"
        elif normalized_entropy >= 0.2:
            score = 40
            status = "low"
        else:
            score = 20
            status = "very_low"
        
        return {
            "score": score,
            "diversity": normalized_entropy,
            "status": status,
            "categories_count": len(category_counts)
        }
    
    async def _get_monthly_expenses(self, transactions: List[Transaction]) -> float:
        """Get average monthly expenses."""
        monthly_expenses = {}
        for txn in transactions:
            if txn.transaction_type == "debit":
                month_key = txn.date.replace(day=1)
                if month_key not in monthly_expenses:
                    monthly_expenses[month_key] = 0
                monthly_expenses[month_key] += abs(float(txn.amount))
        
        if not monthly_expenses:
            return 0
        
        return sum(monthly_expenses.values()) / len(monthly_expenses)
    
    def _calculate_overall_score(self, metrics: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall health score from individual metrics."""
        weights = {
            'income_expense_ratio': 0.25,
            'savings_rate': 0.25,
            'spending_consistency': 0.15,
            'emergency_fund_score': 0.20,
            'debt_management': 0.10,
            'category_diversity': 0.05
        }
        
        total_score = 0
        total_weight = 0
        
        for metric_name, weight in weights.items():
            if metric_name in metrics and 'score' in metrics[metric_name]:
                total_score += metrics[metric_name]['score'] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0
        
        return round(total_score / total_weight, 1)
    
    def _get_health_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        elif score >= 40:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, metrics: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate personalized recommendations based on metrics."""
        recommendations = []
        
        # Income-expense ratio recommendations
        if metrics.get('income_expense_ratio', {}).get('status') in ['concerning', 'critical']:
            recommendations.append("Consider reducing monthly expenses or increasing income to improve your financial health.")
        
        # Savings rate recommendations
        if metrics.get('savings_rate', {}).get('status') in ['fair', 'negative']:
            recommendations.append("Aim to save at least 20% of your income. Start with small amounts and gradually increase.")
        
        # Spending consistency recommendations
        if metrics.get('spending_consistency', {}).get('status') in ['inconsistent', 'highly_inconsistent']:
            recommendations.append("Create a monthly budget to help maintain consistent spending patterns.")
        
        # Emergency fund recommendations
        if metrics.get('emergency_fund_score', {}).get('status') in ['inadequate', 'critical']:
            recommendations.append("Build an emergency fund covering 3-6 months of expenses for financial security.")
        
        # Category diversity recommendations
        if metrics.get('category_diversity', {}).get('status') in ['low', 'very_low']:
            recommendations.append("Diversify your spending categories to better track and manage your finances.")
        
        if not recommendations:
            recommendations.append("Great job! Your financial health is in good shape. Keep maintaining these healthy habits.")
        
        return recommendations
    
    def _get_default_health_score(self) -> Dict[str, Any]:
        """Return default health score when no data is available."""
        return {
            'overall_score': 50,
            'health_grade': 'C',
            'metrics': {
                'income_expense_ratio': {'score': 50, 'status': 'insufficient_data'},
                'savings_rate': {'score': 50, 'status': 'insufficient_data'},
                'spending_consistency': {'score': 50, 'status': 'insufficient_data'},
                'emergency_fund_score': {'score': 50, 'status': 'insufficient_data'},
                'debt_management': {'score': 50, 'status': 'insufficient_data'},
                'category_diversity': {'score': 50, 'status': 'insufficient_data'}
            },
            'recommendations': ['Start adding transactions to get personalized financial health insights.'],
            'calculated_at': datetime.utcnow().isoformat()
        }
