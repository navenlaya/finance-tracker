import pandas as pd
from django.utils import timezone
from .models import Transaction

def generate_budget_insights(user):
    """
    Creates human-readable budget suggestions.
    Example: "You're spending 30% more on Food & Drink this month."
    """

    # Load this user's transactions into DataFrame
    tx = Transaction.objects.filter(user=user)
    if not tx.exists():
        return ["No spending data yet!"]

    df = pd.DataFrame.from_records(tx.values('date', 'category', 'amount'))
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')

    # Group by month and category, sum spending
    monthly = df.groupby(['month', 'category'])['amount'].sum().reset_index()

    # Only keep last two months
    monthly = monthly.sort_values('month').dropna()
    recent_months = monthly['month'].unique()
    if len(recent_months) < 2:
        return ["Need at least 2 months of spending for insights!"]

    this_month = recent_months[-1]
    last_month = recent_months[-2]

    insights = []

    # For each category, compare this month vs last month
    for cat in monthly['category'].unique():
        this_total = monthly[(monthly['month'] == this_month) & (monthly['category'] == cat)]['amount'].sum()
        last_total = monthly[(monthly['month'] == last_month) & (monthly['category'] == cat)]['amount'].sum()

        if last_total == 0:
            continue  # Skip if no spending last month

        pct_change = ((this_total - last_total) / abs(last_total)) * 100

        if abs(pct_change) < 10:
            continue  # Ignore tiny changes

        if pct_change > 0:
            msg = f"You're spending {pct_change:.1f}% MORE on {cat} this month compared to last."
        else:
            msg = f"You're spending {abs(pct_change):.1f}% LESS on {cat} this month. Good job!"

        insights.append(msg)

    if not insights:
        insights = ["No big spending changes detected. Keep it up!"]

    return insights
