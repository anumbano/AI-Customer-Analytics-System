from fastapi import APIRouter, UploadFile, File
import os
import pandas as pd
from services.preprocessing import clean_csv_data
from services.ml_engine import generate_customer_segments, predict_churn, get_recommendations, calculate_avg_revenue
import data_store


router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Clean CSV
    cleaned_data = clean_csv_data(file_path)

    # ML Processing
    segmentation_results = generate_customer_segments(cleaned_data)
    churn_results = predict_churn(cleaned_data)
    recommendation_results = get_recommendations(cleaned_data)
    avg_revenue = calculate_avg_revenue(cleaned_data)

    # Generate Monthly Revenue
    monthly_revenue = {
        "premium": list(cleaned_data.iloc[:,0].head(7)),
        "regular": list(cleaned_data.iloc[:,1].head(7)),
        "occasional": list(cleaned_data.iloc[:,2].head(7))
    }


    # ==============================
    # NEW: Top Customers
    # ==============================
    top_customers_list = []

    if "Purchase_Amount" in cleaned_data.columns:

        top_customers = cleaned_data.sort_values(
            by="Purchase_Amount",
            ascending=False
        ).head(5)

        for _, row in top_customers.iterrows():

            segment = "Regular"

            if row["Purchase_Amount"] > 500:
                segment = "Premium"
            elif row["Purchase_Amount"] < 200:
                segment = "Occasional"

            top_customers_list.append({
                "name": row.get("Name", "Customer"),
                "revenue": float(row["Purchase_Amount"]),
                "segment": segment
            })


    # ==============================
    # NEW: AI Insights
    # ==============================
    churn_percent = churn_results.get("value", 0)
    premium_count = segmentation_results.get("premium", 0)

    ai_insights = [
        f"{churn_percent}% customers likely to churn",
        f"{premium_count} premium customers identified",
        f"{len(cleaned_data)} customers analyzed",
        "Purchase trends detected"
    ]


    # ==============================
    # NEW: Dynamic Recommendations
    # ==============================
    dynamic_recommendations = [
        "Send offers to at-risk customers",
        "Launch loyalty program for premium users",
        "Cross-sell to regular buyers"
    ]

    # Merge ML recommendations + dynamic ones
    final_recommendations = {
        "items": dynamic_recommendations,
        "ml_based": recommendation_results
    }


    # ==============================
    # Final Response (IMPORTANT FIX)
    # ==============================

    data_store.processed_data.clear()
    data_store.processed_data.update({
        "filename": file.filename,
        "segmentation": segmentation_results,
        "churn_prediction": churn_results,
        "recommendations": final_recommendations,
        "total_customers": len(cleaned_data),
        "monthly_revenue": monthly_revenue,
        "top_customers": top_customers_list,
        "ai_insights": ai_insights,
        "avg_revenue_per_customer": avg_revenue
    })


    return data_store.processed_data