import time
import requests
import logging
from django.http import JsonResponse
from concurrent.futures import ThreadPoolExecutor, as_completed
from insights import hf_models as models  # Hugging Face models

import uuid
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
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

# -----------------------------
# Helper functions
# -----------------------------
def safe_request(url: str) -> dict:
    time.sleep(REQUEST_DELAY)
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError as e:
        if res.status_code == 400:
            return {}
        logger.error(f"HTTP error: {url} -> {e}")
    except Exception as e:
        logger.error(f"Request failed: {url} -> {e}")
    return {}

def fetch_profile(token: str) -> dict:
    url = (
        f"https://graph.facebook.com/v19.0/me?"
        f"fields=id,name,birthday,gender,picture.width(200).height(200)"
        f"&access_token={token}"
    )
    return safe_request(url)

def fetch_comments(post_id: str, token: str) -> list:
    comments = []
    next_url = f"https://graph.facebook.com/v19.0/{post_id}/comments?fields=message,created_time,comments&limit=20&access_token={token}"
    while next_url and len(comments) < MAX_COMMENTS:
        data = safe_request(next_url)
        comments.extend(data.get("data", []))
        next_url = data.get("paging", {}).get("next")
    return comments[:MAX_COMMENTS]

def fetch_nested_comments(comment: dict, token: str) -> list:
    nested_comments = []
    if "comments" in comment:
        nested_data = comment["comments"].get("data", [])[:MAX_NESTED]
        for nested in nested_data:
            nested_comments.append(nested)
            nested_comments.extend(fetch_nested_comments(nested, token))
    return nested_comments

# -----------------------------
# Main View
# -----------------------------
def analyze_facebook(request):
    token = request.GET.get("token") or request.COOKIES.get("fb_token")
    method = request.GET.get("method", "ml")
    max_posts = int(request.GET.get("max_posts", DEFAULT_MAX_POSTS))

    if not token:
        return JsonResponse({"error": "Token missing"}, status=401)

    profile_data = fetch_profile(token)
    insights = []
    shared_cache = {}
    fetched_posts = 0

    next_url = f"https://graph.facebook.com/v19.0/me/posts?fields=message,story,status_type,created_time,object_id&limit=10&access_token={token}"

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
                    shared_message = safe_request(
                        f"https://graph.facebook.com/v19.0/{shared_id}?fields=message&access_token={token}"
                    ).get("message", "")
                    shared_cache[shared_id] = shared_message
                content = shared_cache.get(shared_id, content)

            # -----------------------------
            # Analyze post with Hugging Face
            # -----------------------------
            try:
                analysis = analyze_text(content, method)
            except Exception as e:
                logger.error(f"Sentiment analysis failed: {e}")
                analysis = {"original": content, "translated": "", "label": "neutral"}

            # Add extra features
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

            # -----------------------------
            # Analyze comments concurrently
            # -----------------------------
            top_comments = fetch_comments(post["id"], token)
            all_comments = []
            for c in top_comments:
                all_comments.append(c)
                all_comments.extend(fetch_nested_comments(c, token))

            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                futures = {executor.submit(analyze_text, c.get("message", ""), method): c for c in all_comments}
                for future in as_completed(futures):
                    c = futures[future]
                    try:
                        c_analysis = future.result()
                    except Exception as e:
                        logger.error(f"Comment analysis failed: {e}")
                        c_analysis = {"original": c.get("message", ""), "translated": "", "label": "neutral"}

                    c_analysis.update({
                        "timestamp": c.get("created_time"),
                        "is_respectful": is_respectful(c.get("message", "")),
                        "mentions_location": mentions_location(c.get("message", "")),
                        "privacy_disclosure": discloses_personal_info(c.get("message", "")),
                        "toxic": is_toxic(c.get("message", "")),
                        "misinformation_risk": is_potential_misinformation(c.get("message", "")),
                        "type": "comment"
                    })

                    insights.append(c_analysis)

            fetched_posts += 1

        next_url = data.get("paging", {}).get("next")

    # -----------------------------
    # Compute metrics and recommendations
    # -----------------------------
    insightMetrics, recommendations = compute_insight_metrics(insights)

    return JsonResponse({
        "profile": profile_data,
        "insights": insights,
        "insightMetrics": insightMetrics,
        "recommendations": recommendations
    })

@csrf_exempt
@login_required
def request_report(request):
    from .tasks import generate_report  # move import here

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
    generate_report.delay(report_id, token, method, max_posts, user_id=request.user.id)

    return JsonResponse({"report_id": report_id, "status": "pending"})

@login_required
def get_reports(request):
    user_id = str(request.user.id)
    reports = list(reports_collection.find({"user_id": user_id}).sort("created_at", -1))
    for r in reports:
        r["_id"] = str(r["_id"])
    return JsonResponse({"reports": reports})

@login_required
def get_report(request, report_id):
    report = reports_collection.find_one({"report_id": report_id, "user_id": str(request.user.id)})
    if not report:
        return JsonResponse({"error": "Report not found"}, status=404)
    report["_id"] = str(report["_id"])
    return JsonResponse(report)