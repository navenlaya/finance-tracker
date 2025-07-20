from fastapi import APIRouter, Depends, HTTPException
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

router = APIRouter()

@router.get("/forecast")
def forecast_spending(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(PlaidItem).filter_by(user_id=current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No Plaid account linked.")
    try:
        # Get transactions from Plaid
        txns = get_transactions(item.access_token)["transactions"]
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

@router.post("/ai/advice")
def ai_advice(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    question: str = "Give me advice on my spending."
):
    item = db.query(PlaidItem).filter_by(user_id=current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No Plaid account linked.")
    try:
        txns = get_transactions(item.access_token)["transactions"]
        # Summarize spending by category
        summary = {}
        for t in txns:
            cat = t.get("category", ["Other"])[0]
            summary[cat] = summary.get(cat, 0) + t["amount"]
        summary_str = ", ".join([f"{cat}: ${amt:.2f}" for cat, amt in summary.items()])
        # Get forecast
        # (Reuse forecast logic)
        df = pd.DataFrame([
            {"ds": t["date"], "y": t["amount"]} for t in txns if t["amount"] > 0
        ])
        if not df.empty:
            df = df.groupby("ds").sum().reset_index()
            model = Prophet()
            model.fit(df)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            forecast_data = forecast[['ds', 'yhat']].tail(7).to_dict(orient='records')
            forecast_str = ", ".join([f"{f['ds'][:10]}: ${f['yhat']:.2f}" for f in forecast_data])
        else:
            forecast_str = "Not enough data for forecast."
        # Compose prompt
        prompt = (
            f"User's recent spending by category: {summary_str}. "
            f"Spending forecast for next week: {forecast_str}. "
            f"Question: {question} "
            f"Give actionable, friendly financial advice."
        )
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not set.")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        if not response or not hasattr(response, 'choices') or not response.choices or not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise HTTPException(status_code=500, detail="OpenAI did not return a valid response.")
        answer = response.choices[0].message.content.strip()
        return {"advice": answer}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 