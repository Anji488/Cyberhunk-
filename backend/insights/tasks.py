from celery import shared_task
from .mongo_client import reports_collection
from django.test import RequestFactory
from .views import analyze_facebook
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_report(report_id, token, method="ml", max_posts=5, user_id=None):
    try:
        # Step 1: Insert pending report
        reports_collection.insert_one({
            "report_id": report_id,
            "user_id": str(user_id),
            "status": "processing",
            "created_at": datetime.utcnow(),
            "profile_data": {},
            "insights": [],
            "insight_metrics": [],
            "recommendations": []
        })

        # Step 2: Use existing analyze_facebook logic
        factory = RequestFactory()
        request = factory.get("/fake-url", {
            "token": token,
            "method": method,
            "max_posts": max_posts
        })

        response = analyze_facebook(request)
        data = response.json()

        # Step 3: Update report in MongoDB
        reports_collection.update_one(
            {"report_id": report_id},
            {"$set": {
                "status": "completed",
                "profile_data": data.get("profile"),
                "insights": data.get("insights"),
                "insight_metrics": data.get("insightMetrics"),
                "recommendations": data.get("recommendations"),
                "updated_at": datetime.utcnow()
            }}
        )
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        reports_collection.update_one(
            {"report_id": report_id},
            {"$set": {"status": "failed", "error": str(e), "updated_at": datetime.utcnow()}}
        )
