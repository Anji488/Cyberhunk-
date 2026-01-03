from celery import shared_task
from datetime import datetime
import logging

from .mongo_client import reports_collection
from .report_service import analyze_facebook_data

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3}
)
def generate_report(self, report_id, token, method="ml", max_posts=5, user_id=None):

    # Step 1: Create report
    reports_collection.insert_one({
        "report_id": report_id,
        "user_id": str(user_id),
        "profile_id": None,  # will update later
        "status": "processing",
        "created_at": datetime.utcnow()
    })


    try:
        from .report_service import fetch_profile

        profile = fetch_profile(token)
        result = analyze_facebook_data(token, method, max_posts)


        reports_collection.update_one(
            {"report_id": report_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "profile": profile,
                "profile_id": profile.get("id") if profile else None,
                "insights": result["insights"],
                "insightMetrics": result["insightMetrics"],
                "recommendations": result["recommendations"],
            }}
        )




    except Exception as e:
        logger.error(f"Report failed: {e}")

        reports_collection.update_one(
            {"report_id": report_id},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.utcnow()
            }}
        )
        raise
