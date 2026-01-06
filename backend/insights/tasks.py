from celery import shared_task
from datetime import datetime
import logging

from .mongo_client import reports_collection
from .report_service import analyze_facebook_data, fetch_profile

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_report(self, report_id, token, method="ml", max_posts=5, user_id=None):

    logger.info(f"📝 Creating report | report_id={report_id}")

    try:
        # 1️⃣ FETCH PROFILE FIRST (CRITICAL)
        profile = fetch_profile(token)
        if not profile or not profile.get("id"):
            raise Exception("Unable to fetch Facebook profile")

        profile_id = profile["id"]

        # 2️⃣ PREVENT DUPLICATE COMPLETED REPORTS
        existing = reports_collection.find_one({
            "profile_id": profile_id,
            "status": "completed"
        })

        if existing:
            logger.info(
                f"⚠️ Completed report already exists for profile_id={profile_id}"
            )
            return

        # 3️⃣ INSERT REPORT (profile_id KNOWN)
        reports_collection.insert_one({
            "report_id": report_id,
            "user_id": str(user_id) if user_id else None,
            "profile_id": profile_id,
            "status": "processing",
            "created_at": datetime.utcnow()
        })

        logger.info("✅ Report record created")

        # 4️⃣ RUN ANALYSIS
        analysis = analyze_facebook_data(token, method, max_posts)

        # 5️⃣ UPDATE REPORT
        reports_collection.update_one(
            {"report_id": report_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "profile": profile,
                "insights": analysis["insights"],
                "insightMetrics": analysis["insightMetrics"],
                "recommendations": analysis["recommendations"]
            }}
        )

        logger.info(f"✅ Report completed | report_id={report_id}")

    except Exception as e:
        logger.exception("❌ Report generation failed")

        reports_collection.update_one(
            {"report_id": report_id},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.utcnow()
            }}
        )
