from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.security import get_current_user, get_db
from app.models.user import User
from app.models.plaid import PlaidItem
from app.core.security import decrypt_token
import pandas as pd
from prophet import Prophet
import datetime
from app.services.plaid import get_transactions
import openai
import os
from pydantic import BaseModel

router = APIRouter()

@router.get("/forecast")
def forecast_spending(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(PlaidItem).filter_by(user_id=current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No Plaid account linked.")
    try:
        txns_response = get_transactions(item.access_token)
        if not txns_response or "transactions" not in txns_response:
            raise HTTPException(status_code=400, detail="Could not fetch transactions from Plaid.")
        txns = txns_response["transactions"]
        # TEMP: Include all positive-amount transactions for testing
        df = pd.DataFrame([
            {"ds": t["date"], "y": t["amount"]}
            for t in txns
            if t["amount"] > 0
        ])
        # Cap outliers (e.g., $1000/day)
        if not df.empty:
            df["y"] = df["y"].clip(upper=1000)
        print("Forecast DataFrame:", df)
        if df.empty:
            raise HTTPException(status_code=400, detail="Not enough data for forecasting.")
        df = df.groupby("ds").sum().reset_index()
        # Prophet expects daily data
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        # Return only the forecasted values
        forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30).to_dict(orient='records')
        return {"forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 