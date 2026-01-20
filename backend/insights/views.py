import time
import requests
import logging
from django.http import JsonResponse
from concurrent.futures import ThreadPoolExecutor, as_completed

import uuid
import json
from django.http import HttpResponse
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




MAX_THREADS = 5
REQUEST_DELAY = 0.3
DEFAULT_MAX_POSTS = 5
MAX_COMMENTS = 5
MAX_POSTS_LIMIT = 5
MAX_COMMENTS_LIMIT = 5
MAX_NESTED = 5

def robots_txt(request):
    lines = [
        "User-agent: facebookexternalhit",
        "Allow: /",
        "User-agent: *",
        "Allow: /",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

logger = logging.getLogger(__name__)


# Helper functions

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


# CORS SAFE JSON RESPONSE HELPER

def cors_json_response(data, status=200):
    """Ensures CORS headers are present even if the view catches an error."""
    response = JsonResponse(data, status=status)
    # Match your frontend Vercel URL
    response["Access-Control-Allow-Origin"] = "https://cyberhunk.vercel.app"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# Main View

@csrf_exempt
def analyze_facebook(request):
    if request.method == "OPTIONS":
        return cors_json_response({})

    if request.method != "GET":
        return cors_json_response({"error": "Method not allowed"}, status=405)

    try:
        
        # Auth
        
        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

        token = token or request.GET.get("token") or request.COOKIES.get("fb_token")

        if not token:
            return cors_json_response({"error": "Authorization token missing"}, status=401)

        method = request.GET.get("method", "ml")

        # 🔒 HARD SAFETY LIMIT (DO NOT REMOVE)
        MAX_ML_POSTS = 1
        max_posts = min(int(request.GET.get("max_posts", 1)), MAX_ML_POSTS)

        
        # Verify Token
        
        profile_res = requests.get(
            "https://graph.facebook.com/v19.0/me",
            params={
                "fields": "id,name,birthday,gender,picture.width(200).height(200)",
                "access_token": token
            },
            timeout=10
        )

        if profile_res.status_code != 200:
            return cors_json_response(
                {"error": "Facebook rejected token or expired"},
                status=401
            )

        profile_data = profile_res.json()

        
        # Fetch Posts
        
        insights = []
        fetched_posts = 0

        fb_posts_url = (
            f"https://graph.facebook.com/v19.0/me/posts?"
            f"fields=message,story,status_type,created_time,object_id"
            f"&limit={max_posts}&access_token={token}"
        )

        res = requests.get(fb_posts_url, timeout=30)
        if res.status_code != 200:
            raise Exception("Failed to fetch Facebook posts")

        posts = res.json().get("data", [])

        for post in posts:
            if fetched_posts >= max_posts:
                break

            content = post.get("message") or post.get("story") or ""

            
            # 🔥 SINGLE ML CALL (CRITICAL)
            
            try:
                ml_result = analyze_text(content, method)
            except Exception as e:
                logger.warning(f"ML failed, falling back: {e}")
                ml_result = {
                    "original": content,
                    "label": "neutral",
                    "toxic": False,
                    "misinformation": False,
                }

            insight = {
                **ml_result,
                "timestamp": post.get("created_time"),
                "status_type": post.get("status_type"),
                "type": "post",

                # ✅ Reuse ML result (NO NEW CALLS)
                "is_respectful": not ml_result.get("toxic", False),
                "mentions_location": mentions_location(content),
                "privacy_disclosure": discloses_personal_info(content),
                "toxic": ml_result.get("toxic", False),
                "misinformation_risk": ml_result.get("misinformation", False),
            }

            insights.append(insight)
            fetched_posts += 1

            time.sleep(REQUEST_DELAY)

        
        # Final Metrics
        
        insight_metrics, recommendations = compute_insight_metrics(insights)

        return cors_json_response({
            "profile": profile_data,
            "insights": insights,
            "insightMetrics": insight_metrics,
            "recommendations": recommendations
        })

    except Exception as e:
        logger.error(f"SYSTEM CRASH: {e}", exc_info=True)
        return cors_json_response(
            {"error": "Internal Server Error", "details": str(e)},
            status=500
        )

@csrf_exempt
def request_report(request):
    from .tasks import generate_report

    logger.info("➡️ /insights/request-report CALLED")

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except Exception as e:
        logger.error(f"Invalid JSON body: {e}")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    token = data.get("token")
    method = data.get("method", "ml")
    max_posts = int(data.get("max_posts", 5))

    if not token:
        return JsonResponse({"error": "Token required"}, status=400)

    report_id = str(uuid.uuid4())

    # NOW THIS IS SAFE
    logger.info(f"Starting report generation | report_id={report_id}")

    try:
        generate_report(
            report_id,
            token,
            method,
            max_posts,
            user_id=None
        )
    except Exception as e:
        logger.error(f"Celery dispatch failed: {e}")
        return JsonResponse({"error": "Report queue unavailable"}, status=503)

    return JsonResponse({
        "report_id": report_id,
        "status": "pending"
    })

@csrf_exempt
def get_reports(request):
    profile_id = request.GET.get("profile_id")

    if not profile_id:
        return JsonResponse({"reports": []})

    reports = list(
        reports_collection
        .find({"profile_id": profile_id})
        .sort("created_at", -1)
    )

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

@csrf_exempt
def ping_facebook(request):
    try:
        r = requests.get("https://graph.facebook.com", timeout=5)
        return JsonResponse({"status": r.status_code})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
