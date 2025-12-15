import time
import uuid
import json
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

# ==========================
# CONFIG
# ==========================
MAX_THREADS = 5
REQUEST_DELAY = 0.3
DEFAULT_MAX_POSTS = 100
MAX_COMMENTS = 100
MAX_NESTED = 5

# ==========================
# SAFE REQUEST
# ==========================
def safe_request(url: str) -> dict:
    time.sleep(REQUEST_DELAY)
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        logger.error(f"[FB REQUEST FAILED] {url} -> {e}")
        return {}

# ==========================
# FACEBOOK HELPERS
# ==========================
def fetch_profile(token: str) -> dict:
    return safe_request(
        "https://graph.facebook.com/v19.0/me"
        "?fields=id,name,birthday,gender,picture.width(200).height(200)"
        f"&access_token={token}"
    )

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
    nested = []
    replies = comment.get("comments", {}).get("data", [])[:MAX_NESTED]
    for r in replies:
        nested.append(r)
        nested.extend(fetch_nested_comments(r, token))
    return nested

# ==========================
# MAIN VIEW
# ==========================
def analyze_facebook(request):
    try:
        token = request.GET.get("token") or request.COOKIES.get("fb_token")
        method = request.GET.get("method", "ml")
        max_posts = int(request.GET.get("max_posts", DEFAULT_MAX_POSTS))

        if not token:
            return JsonResponse({"error": "Token missing"}, status=401)

        profile = fetch_profile(token)
        if not profile or "error" in profile:
            return JsonResponse({"error": "Invalid Facebook token"}, status=401)

        insights = []
        fetched_posts = 0
        shared_cache = {}

        # 🔁 TRY POSTS FIRST
        next_url = (
            f"https://graph.facebook.com/v19.0/me/posts"
            f"?fields=message,story,status_type,created_time,object_id"
            f"&limit=10&access_token={token}"
        )

        data = safe_request(next_url)

        # 🔁 FALLBACK TO FEED IF POSTS EMPTY
        if not data.get("data"):
            logger.warning("⚠️ /me/posts empty → switching to /me/feed")
            next_url = (
                f"https://graph.facebook.com/v19.0/me/feed"
                f"?fields=message,story,created_time"
                f"&limit=10&access_token={token}"
            )

        while next_url and fetched_posts < max_posts:
            data = safe_request(next_url)
            posts = data.get("data", [])

            if not posts and fetched_posts == 0:
                return JsonResponse({
                    "profile": profile,
                    "insights": [],
                    "insightMetrics": [],
                    "recommendations": [],
                    "warning": "No Facebook posts returned. Missing user_posts permission."
                })

            for post in posts:
                if fetched_posts >= max_posts:
                    break

                content = post.get("message") or post.get("story") or ""

                if not content.strip():
                    continue

                # ANALYZE POST
                try:
                    analysis = analyze_text(content, method)
                except Exception:
                    analysis = {"original": content, "translated": "", "label": "neutral"}

                analysis.update({
                    "timestamp": post.get("created_time"),
                    "is_respectful": is_respectful(content),
                    "mentions_location": mentions_location(content),
                    "privacy_disclosure": discloses_personal_info(content),
                    "toxic": is_toxic(content),
                    "misinformation_risk": is_potential_misinformation(content),
                    "type": "post"
                })

                insights.append(analysis)

                # COMMENTS
                if post.get("id"):
                    top_comments = fetch_comments(post["id"], token)
                    all_comments = []
                    for c in top_comments:
                        all_comments.append(c)
                        all_comments.extend(fetch_nested_comments(c, token))

                    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                        futures = {
                            executor.submit(analyze_text, c.get("message", ""), method): c
                            for c in all_comments
                        }
                        for future in as_completed(futures):
                            c = futures[future]
                            msg = c.get("message", "")
                            if not msg.strip():
                                continue
                            try:
                                c_analysis = future.result()
                            except Exception:
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

        # METRICS
        insightMetrics, recommendations = compute_insight_metrics(insights)

        # SAVE REPORT
        report_id = str(uuid.uuid4())
        reports_collection.insert_one({
            "report_id": report_id,
            "profile": profile,
            "insights": insights,
            "insightMetrics": insightMetrics,
            "recommendations": recommendations,
            "created_at": time.time()
        })

        return JsonResponse({
            "report_id": report_id,
            "profile": profile,
            "insights": insights,
            "insightMetrics": insightMetrics,
            "recommendations": recommendations
        })

    except Exception as e:
        logger.exception("Analyze Facebook failed")
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
