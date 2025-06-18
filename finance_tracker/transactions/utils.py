# transactions/utils.py

# Rule-based transaction categorization

def categorize(description):
    desc = description.lower()

    if 'coffee' in desc or 'starbucks' in desc:
        return 'Food & Drink'
    elif 'uber' in desc or 'lyft' in desc:
        return 'Transport'
    elif 'amazon' in desc:
        return 'Shopping'
    elif 'grocery' in desc or 'market' in desc:
        return 'Groceries'
    elif 'rent' in desc or 'apartment' in desc:
        return 'Housing'
    elif 'salary' in desc or 'paycheck' in desc:
        return 'Income'
    else:
        return 'Uncategorized'
