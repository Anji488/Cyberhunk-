import time
import uuid
import json
import logging
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from concurrent.futures import ThreadPoolExecutor, as_completed

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
MAX_THREADS = 5
REQUEST_DELAY = 0.3
DEFAULT_MAX_POSTS = 100
MAX_COMMENTS = 100
MAX_NESTED = 5


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

        try:
            return res.json()
        except ValueError:
            logger.error(f"[FB INVALID JSON] {res.text[:200]}")
            return {}

    except requests.exceptions.RequestException as e:
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


def fetch_comments(post_id: str, token: str) -> list:
    comments = []
    next_url = (
        f"https://graph.facebook.com/v19.0/{post_id}/comments"
        "?fields=message,created_time,comments"
        f"&limit=20&access_token={token}"
    )

    while next_url and len(comments) < MAX_COMMENTS:
        data = safe_request(next_url)
        comments.extend(data.get("data", []))
        next_url = data.get("paging", {}).get("next")

    return comments[:MAX_COMMENTS]


def fetch_nested_comments(comment: dict, token: str) -> list:
    """Recursively fetch nested replies up to MAX_NESTED depth."""
    nested_comments = []

    replies = comment.get("comments", {}).get("data", [])
    replies = replies[:MAX_NESTED]

    for nested in replies:
        nested_comments.append(nested)
        nested_comments.extend(fetch_nested_comments(nested, token))

    return nested_comments


# ===================================
# MAIN ANALYSIS VIEW
# ===================================
@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def analyze_facebook(request):

    # ✅ Handle CORS preflight
    if request.method == "OPTIONS":
        response = JsonResponse({}, status=200)
        response["Access-Control-Allow-Origin"] = "https://cyberhunk.vercel.app"
        response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    # ✅ Read token ONLY from Authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return JsonResponse(
            {"error": "Authorization token missing"},
            status=401
        )

    token = auth_header.split(" ", 1)[1]
    method = request.GET.get("method", "ml")

    try:
        max_posts = int(request.GET.get("max_posts", DEFAULT_MAX_POSTS))
    except ValueError:
        max_posts = DEFAULT_MAX_POSTS

    # =========================
    # FETCH PROFILE
    # =========================
    profile_data = fetch_profile(token)
    if not profile_data:
        return JsonResponse({"error": "Invalid Facebook token"}, status=401)

    insights = []
    shared_cache = {}
    fetched_posts = 0

    next_url = (
        "https://graph.facebook.com/v19.0/me/posts?"
        "fields=message,story,status_type,created_time,object_id"
        f"&limit=10&access_token={token}"
    )

    while next_url and fetched_posts < max_posts:
        data = safe_request(next_url)
        posts = data.get("data", [])

        for post in posts:
            if fetched_posts >= max_posts:
                break

            content = post.get("message") or post.get("story") or ""

            if post.get("status_type") == "shared_story":
                shared_id = post.get("object_id")
                if shared_id and shared_id not in shared_cache:
                    shared_cache[shared_id] = safe_request(
                        f"https://graph.facebook.com/v19.0/{shared_id}"
                        f"?fields=message&access_token={token}"
                    ).get("message", "")
                content = shared_cache.get(shared_id, content)

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

    insightMetrics, recommendations = compute_insight_metrics(insights)

    return JsonResponse({
        "profile": profile_data,
        "insights": insights,
        "insightMetrics": insightMetrics,
        "recommendations": recommendations
    })

# ===================================
# SAVED REPORTS API
# ===================================
@csrf_exempt
def request_report(request):
    from .tasks import generate_report

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    token = data.get("token")
    method = data.get("method", "ml")
    max_posts = int(data.get("max_posts", 100))

    if not token:
        return JsonResponse({"error": "Token required"}, status=400)

    report_id = str(uuid.uuid4())
    user_id = str(request.user.id) if getattr(request.user, "is_authenticated", False) else "guest"

    generate_report.delay(report_id, token, method, max_posts, user_id=user_id)

    return JsonResponse({"report_id": report_id, "status": "pending"})


@csrf_exempt
def get_reports(request):
    user_id = str(request.user.id) if getattr(request.user, "is_authenticated", False) else None
    if not user_id:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    profile_id = request.GET.get("profile_id")
    query = {"user_id": user_id}

    if profile_id:
        query["profile.id"] = profile_id

    reports = list(reports_collection.find(query).sort("created_at", -1))

    for r in reports:
        r["_id"] = str(r["_id"])

    return JsonResponse({"reports": reports})


@csrf_exempt
def get_report(request, report_id):
    report = reports_collection.find_one({"report_id": report_id})

    if not report:
        return JsonResponse({"error": "Report not found"}, status=404)

    report["_id"] = str(report["_id"])
    return JsonResponse(report)
