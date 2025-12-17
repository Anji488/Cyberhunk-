import time
import uuid
import json
import logging
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .mongo_client import reports_collection
from insights.services import (
    analyze_text,
    is_respectful,
    mentions_location,
    discloses_personal_info,
    is_toxic,
    is_potential_misinformation,
    compute_insight_metrics
)

logger = logging.getLogger(__name__)

# ===================================
# CONFIG
# ===================================
REQUEST_DELAY = 0.3
DEFAULT_MAX_POSTS = 100
MAX_COMMENTS = 100
MAX_NESTED = 5
FRONTEND_ORIGIN = "https://cyberhunk.vercel.app"
from django.views.decorators.csrf import csrf_exempt


# ===================================
# SAFE REQUEST WRAPPER
# ===================================
def safe_request(url: str) -> dict:
    time.sleep(REQUEST_DELAY)
    try:
        res = requests.get(url, timeout=8)

        if res.status_code != 200:
            logger.error(f"[FB ERROR] {res.status_code} -> {res.text[:200]}")
            return {}

        return res.json()

    except Exception as e:
        logger.error(f"[REQUEST FAIL] {url} -> {e}")
        return {}


# ===================================
# FACEBOOK API HELPERS
# ===================================
def fetch_profile(token: str) -> dict:
    url = (
        "https://graph.facebook.com/v19.0/me?"
        "fields=id,name,birthday,gender,picture.width(200).height(200)"
        f"&access_token={token}"
    )
    return safe_request(url)


# ===================================
# MAIN ANALYSIS VIEW
# ===================================
@@csrf_exempt
def analyze_facebook(request):

    if request.method == "OPTIONS":
        return JsonResponse({}, status=200)

    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse({"error": "Authorization token missing"}, status=401)

    token = auth_header.split(" ", 1)[1]
    method = request.GET.get("method", "ml")

    try:
        max_posts = int(request.GET.get("max_posts", 100))
    except ValueError:
        max_posts = 100

    profile_data = fetch_profile(token)
    if not profile_data:
        return JsonResponse({"error": "Invalid Facebook token"}, status=401)

    insights = []
    fetched_posts = 0

    next_url = (
        "https://graph.facebook.com/v19.0/me/posts?"
        "fields=message,story,status_type,created_time"
        f"&limit=10&access_token={token}"
    )

    while next_url and fetched_posts < max_posts:
        data = safe_request(next_url)
        posts = data.get("data", [])

        for post in posts:
            if fetched_posts >= max_posts:
                break

            content = post.get("message") or post.get("story") or ""

            analysis = analyze_text(content, method)
            analysis.update({
                "timestamp": post.get("created_time"),
                "is_respectful": is_respectful(content),
                "mentions_location": mentions_location(content),
                "privacy_disclosure": discloses_personal_info(content),
                "toxic": is_toxic(content),
                "misinformation_risk": is_potential_misinformation(content),
                "status_type": post.get("status_type"),
                "type": "post"
            })

            insights.append(analysis)
            fetched_posts += 1

        next_url = data.get("paging", {}).get("next")

    insight_metrics, recommendations = compute_insight_metrics(insights)

    return JsonResponse({
        "profile": profile_data,
        "insights": insights,
        "insightMetrics": insight_metrics,
        "recommendations": recommendations
    }, status=200)

# ===================================
# SAVED REPORTS API
# ===================================
@csrf_exempt
def request_report(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return cors_json({"error": "Invalid JSON"}, 400)

    token = data.get("token")
    method = data.get("method", "ml")
    max_posts = int(data.get("max_posts", 100))

    if not token:
        return cors_json({"error": "Token required"}, 400)

    report_id = str(uuid.uuid4())
    user_id = (
        str(request.user.id)
        if getattr(request.user, "is_authenticated", False)
        else "guest"
    )

    from .tasks import generate_report
    generate_report.delay(report_id, token, method, max_posts, user_id=user_id)

    return cors_json({"report_id": report_id, "status": "pending"})


@csrf_exempt
def get_reports(request):
    user_id = (
        str(request.user.id)
        if getattr(request.user, "is_authenticated", False)
        else None
    )

    if not user_id:
        return cors_json({"error": "Not authenticated"}, 401)

    profile_id = request.GET.get("profile_id")
    query = {"user_id": user_id}

    if profile_id:
        query["profile.id"] = profile_id

    reports = list(reports_collection.find(query).sort("created_at", -1))
    for r in reports:
        r["_id"] = str(r["_id"])

    return cors_json({"reports": reports})


@csrf_exempt
def get_report(request, report_id):
    report = reports_collection.find_one({"report_id": report_id})

    if not report:
        return cors_json({"error": "Report not found"}, 404)

    report["_id"] = str(report["_id"])
    return cors_json(report)
