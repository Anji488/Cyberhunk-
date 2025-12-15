import time
import uuid
import json
import logging
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
    """Performs a safe GET request with logging."""
    time.sleep(REQUEST_DELAY)
    try:
        res = requests.get(url, timeout=8)
        res.raise_for_status()
        return res.json()

    except requests.exceptions.HTTPError:
        if res.status_code == 400:
            return {}
        logger.error(f"[HTTP ERROR] {url}")
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
import time
import uuid
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.http import JsonResponse
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

MAX_THREADS = 5
REQUEST_DELAY = 0.3
DEFAULT_MAX_POSTS = 100
MAX_COMMENTS = 100
MAX_NESTED = 5


def safe_request(url: str) -> dict:
    """Performs a safe GET request with logging."""
    time.sleep(REQUEST_DELAY)
    try:
        res = requests.get(url, timeout=8)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        if res.status_code == 400:
            return {}
        logger.error(f"[HTTP ERROR] {url}")
    except Exception as e:
        logger.error(f"[REQUEST FAIL] {url} -> {e}")
    return {}


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
    nested_comments = []
    replies = comment.get("comments", {}).get("data", [])[:MAX_NESTED]
    for nested in replies:
        nested_comments.append(nested)
        nested_comments.extend(fetch_nested_comments(nested, token))
    return nested_comments


def analyze_facebook(request):
    try:
        token = request.GET.get("token") or request.COOKIES.get("fb_token")
        method = request.GET.get("method", "ml")
        try:
            max_posts = int(request.GET.get("max_posts", DEFAULT_MAX_POSTS))
        except ValueError:
            max_posts = DEFAULT_MAX_POSTS

        if not token:
            return JsonResponse({"error": "Token missing"}, status=401)

        profile_data = fetch_profile(token)
        if not profile_data or "error" in profile_data:
            return JsonResponse({"error": "Invalid or expired Facebook token"}, status=401)

        insights = []
        shared_cache = {}
        fetched_posts = 0

        next_url = (
            f"https://graph.facebook.com/v19.0/me/posts?"
            f"fields=message,story,status_type,created_time,object_id"
            f"&limit=10&access_token={token}"
        )

        while next_url and fetched_posts < max_posts:
            data = safe_request(next_url)
            posts = data.get("data") or []

            for post in posts:
                if fetched_posts >= max_posts:
                    break

                content = post.get("message") or post.get("story") or ""

                # Handle shared stories
                if post.get("status_type") == "shared_story":
                    shared_id = post.get("object_id")
                    if shared_id and shared_id not in shared_cache:
                        shared_msg = safe_request(
                            f"https://graph.facebook.com/v19.0/{shared_id}?fields=message&access_token={token}"
                        ).get("message", "")
                        shared_cache[shared_id] = shared_msg
                    content = shared_cache.get(shared_id, content)

                # Analyze post
                try:
                    analysis = analyze_text(content, method)
                except Exception as e:
                    logger.error(f"Post analysis failed: {e}")
                    analysis = {"original": content, "translated": "", "label": "neutral"}

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

                # Fetch comments + nested
                top_comments = fetch_comments(post.get("id") or "", token) or []
                all_comments = []
                for c in top_comments:
                    all_comments.append(c)
                    all_comments.extend(fetch_nested_comments(c, token))

                # Multithread comment sentiment
                with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                    futures = {executor.submit(analyze_text, c.get("message", ""), method): c for c in all_comments}
                    for future in as_completed(futures):
                        c = futures[future]
                        msg = c.get("message", "")
                        try:
                            c_analysis = future.result()
                        except Exception as e:
                            logger.error(f"Comment analysis failed: {e}")
                            c_analysis = {"original": msg, "translated": "", "label": "neutral"}
                        c_analysis.update({
                            "timestamp": c.get("created_time"),
                            "is_respectful": is_respectful(msg),
                            "mentions_location": mentions_location(msg),
                            "privacy_disclosure": discloses_personal_info(msg),
                            "toxic": is_toxic(msg),
                            "misinformation_risk": is_potential_misinformation(msg),
                            "type": "comment"
                        })
                        insights.append(c_analysis)

                fetched_posts += 1

            next_url = data.get("paging", {}).get("next")

        # Compute metrics
        insightMetrics, recommendations = compute_insight_metrics(insights)

        # Auto-save report
        report_id = str(uuid.uuid4())
        user_id = str(request.user.id) if getattr(request.user, "is_authenticated", False) else "guest"

        report_doc = {
            "report_id": report_id,
            "user_id": user_id,
            "profile": profile_data,
            "insights": insights,
            "insightMetrics": insightMetrics,
            "recommendations": recommendations,
            "created_at": time.time()
        }
        reports_collection.insert_one(report_doc)

        return JsonResponse({
            "report_id": report_id,
            "profile": profile_data,
            "insights": insights,
            "insightMetrics": insightMetrics,
            "recommendations": recommendations
        })

    except Exception as e:
        logger.exception("Unexpected error in analyze_facebook")
        return JsonResponse({"error": str(e)}, status=500)


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
