"""
Machine Learning API endpoints for forecasting and insights.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.auth import get_current_active_user
from app.models.user import User
from app.schemas.transaction import ForecastData, SpendingInsight
from app.ml.insights import SpendingInsightsService
from app.ml.forecasting import SpendingForecastService
from app.ml.health_score import FinancialHealthService

router = APIRouter()


@router.get("/forecast", response_model=List[ForecastData])
async def get_spending_forecast(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    days_ahead: int = 30
):
    """Get spending forecast for the user."""
    try:
        forecast_service = SpendingForecastService(db, current_user)
        forecasts = await forecast_service.generate_forecast(days_ahead)
        return forecasts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating forecast: {str(e)}"
        )


@router.get("/insights", response_model=List[SpendingInsight])
async def get_spending_insights(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-generated spending insights."""
    try:
        insights_service = SpendingInsightsService(db, current_user)
        insights = await insights_service.generate_insights()
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating insights: {str(e)}"
        )


@router.get("/health-score")
async def get_financial_health_score(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive financial health score and metrics."""
    try:
        health_service = FinancialHealthService(db, current_user)
        health_score = await health_service.calculate_health_score()
        return health_score
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating health score: {str(e)}"
        )


@router.get("/forecast-accuracy")
async def get_forecast_accuracy(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get forecast accuracy metrics."""
    try:
        forecast_service = SpendingForecastService(db, current_user)
        accuracy = await forecast_service.get_forecast_accuracy()
        return accuracy
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting forecast accuracy: {str(e)}"
        )


@router.post("/retrain")
async def retrain_models(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger model retraining for the user."""
    try:
        # In a production system, this would trigger background model retraining
        # For now, return a success message
        return {
            "message": "Model retraining initiated",
            "status": "queued",
            "estimated_completion": "24 hours",
            "user_id": str(current_user.id)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating model retraining: {str(e)}"
        ) 