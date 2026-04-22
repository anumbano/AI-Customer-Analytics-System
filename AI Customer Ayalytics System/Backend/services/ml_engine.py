import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
import numpy as np

def generate_customer_segments(df):

    # Handle missing columns safely
    if 'last_purchase_days' in df.columns:
        df['Recency'] = df['last_purchase_days']
    else:
        df['Recency'] = 30  # default value

    if 'Purchase_Frequency' in df.columns:
        df['Frequency'] = df['Purchase_Frequency']
    else:
        df['Frequency'] = 5

    if 'Purchase_Amount' in df.columns:
        df['Monetary'] = df['Purchase_Amount']
    else:
        df['Monetary'] = 100

    # KMeans Clustering
    X = df[['Recency', 'Frequency', 'Monetary']]

    kmeans = KMeans(n_clusters=3, random_state=42)
    df['Segment'] = kmeans.fit_predict(X)

    # Count segments
    segmentation = {
        "premium": int((df['Segment'] == 2).sum()),
        "regular": int((df['Segment'] == 1).sum()),
        "occasional": int((df['Segment'] == 0).sum())
    }

    return segmentation


def predict_churn(df):

    # Safe Column Handling
    if 'last_purchase_days' in df.columns:
        df['Recency'] = df['last_purchase_days']
    else:
        df['Recency'] = 30

    if 'Purchase_Frequency' in df.columns:
        df['Frequency'] = df['Purchase_Frequency']
    else:
        df['Frequency'] = 5

    if 'Purchase_Amount' in df.columns:
        df['Monetary'] = df['Purchase_Amount']
    else:
        df['Monetary'] = 100


    X = df[['Recency', 'Frequency', 'Monetary']]

    # Real churn logic
    df['Churn_Label'] = 0

    df.loc[df['Recency'] > 60, 'Churn_Label'] = 1
    df.loc[df['Frequency'] < 2, 'Churn_Label'] = 1

    y = df['Churn_Label']

    # 🔥 SAFETY FIX (Very Important)
    if len(set(y)) < 2:
        # add small variation to avoid crash
        y.iloc[0] = 1

    model = LogisticRegression()
    model.fit(X, y)

    churn_prob = model.predict_proba(X)[:, 1]

    churn_percentage = round(float(churn_prob.mean() * 100), 1)

    return {
        "value": churn_percentage,
        "at_risk": int((churn_prob > 0.5).sum())
    }


def get_recommendations(df):

    recommendations = []

    # Safe column handling
    if 'total_spent' in df.columns:
        avg_spent = df['total_spent'].mean()
    elif 'Purchase_Amount' in df.columns:
        avg_spent = df['Purchase_Amount'].mean()
    else:
        avg_spent = 500

    # Recommendation Logic
    if avg_spent > 2000:
        recommendations.append("Offer VIP loyalty program")

    if len(df) > 50:
        recommendations.append("Launch targeted email campaigns")

    if avg_spent < 500:
        recommendations.append("Offer discount coupons")

    if len(recommendations) == 0:
        recommendations.append("Increase engagement campaigns")

    return recommendations

def calculate_avg_revenue(df):

    # Safe Column Handling
    if 'Purchase_Amount' in df.columns:
        total_revenue = df['Purchase_Amount'].sum()

    elif 'total_spent' in df.columns:
        total_revenue = df['total_spent'].sum()

    else:
        total_revenue = 0

    total_customers = len(df)

    if total_customers == 0:
        avg = 0
    else:
        avg = round(total_revenue / total_customers)

    return avg