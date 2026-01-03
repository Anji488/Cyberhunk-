import time
import requests
import logging
from django.http import JsonResponse
from concurrent.futures import ThreadPoolExecutor, as_completed
from insights import hf_models as models  # Hugging Face models

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

# ===================================
# CORS SAFE JSON RESPONSE HELPER
# ===================================
def cors_json_response(data, status=200):
    """Ensures CORS headers are present even if the view catches an error."""
    response = JsonResponse(data, status=status)
    # Match your frontend Vercel URL
    response["Access-Control-Allow-Origin"] = "https://cyberhunk.vercel.app"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# -----------------------------
# Main View
# -----------------------------
@csrf_exempt
def analyze_facebook(request):
    # 1. Handle Preflight OPTIONS request (Required for CORS)
    if request.method == "OPTIONS":
        return cors_json_response({})

    if request.method != "GET":
        return cors_json_response({"error": "Method not allowed"}, status=405)

    try:
        # 2. Flexible Token Extraction (Fixes the 401 issue)
        token = None
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        
        # Fallbacks
        token = token or request.GET.get("token") or request.COOKIES.get("fb_token")

        if not token:
            logger.error("401 Trace: No token found in headers, params, or cookies")
            return cors_json_response({"error": "Authorization token missing"}, status=401)

        method = request.GET.get("method", "ml")
        max_posts = min(int(request.GET.get("max_posts", 10)), MAX_POSTS_LIMIT)

        # 3. Fetch Profile (Verify Token with FB)
        profile_url = (
            f"https://graph.facebook.com/v19.0/me?"
            f"fields=id,name,birthday,gender,picture.width(200).height(200)"
            f"&access_token={token}"
        )
        profile_res = requests.get(profile_url, timeout=10)
        
        if profile_res.status_code != 200:
            logger.error(f"FB API Error: {profile_res.text}")
            return cors_json_response({"error": "Facebook rejected token or it expired"}, status=401)
        
        profile_data = profile_res.json()

        # 4. Fetch Posts & Sequential Analysis
        insights = []
        shared_cache = {}
        fetched_posts = 0
        
        fb_posts_url = (
            f"https://graph.facebook.com/v19.0/me/posts?"
            f"fields=message,story,status_type,created_time,object_id&limit=5&access_token={token}"
        )

        while fb_posts_url and fetched_posts < max_posts:
            res = requests.get(fb_posts_url, timeout=30)
            if res.status_code != 200: break
            
            data = res.json()
            posts = data.get("data", [])

            for post in posts:
                if fetched_posts >= max_posts: break
                
                content = post.get("message") or post.get("story") or ""
                
                # Handle shared stories
                if post.get("status_type") == "shared_story":
                    shared_id = post.get("object_id")
                    if shared_id and shared_id not in shared_cache:
                        shared_data = requests.get(
                            f"https://graph.facebook.com/v19.0/{shared_id}?fields=message&access_token={token}",
                            timeout=5
                        ).json()
                        shared_cache[shared_id] = shared_data.get("message", "")
                    content = shared_cache.get(shared_id, content)

                # ML Analysis (Post)
                try:
                    analysis = analyze_text(content, method)
                except Exception as e:
                    logger.warning(f"ML Analysis failed: {e}")
                    analysis = {"original": content, "label": "neutral"}

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

                # 5. Fetch & Analyze Comments (Sequential to avoid OOM crash)
                comment_url = (
                    f"https://graph.facebook.com/v19.0/{post['id']}/comments?"
                    f"fields=message,created_time&limit={MAX_COMMENTS_LIMIT}&access_token={token}"
                )
                c_res = requests.get(comment_url, timeout=20)
                if c_res.status_code == 200:
                    for c in c_res.json().get("data", []):
                        c_text = c.get("message", "")
                        try:
                            c_analysis = analyze_text(c_text, method)
                        except:
                            c_analysis = {"original": c_text, "label": "neutral"}
                        
                        c_analysis.update({
                            "timestamp": c.get("created_time"),
                            "is_respectful": is_respectful(c_text),
                            "mentions_location": mentions_location(c_text),
                            "privacy_disclosure": discloses_personal_info(c_text),
                            "toxic": is_toxic(c_text),
                            "type": "comment"
                        })
                        insights.append(c_analysis)
                
                fetched_posts += 1
                time.sleep(REQUEST_DELAY)

            fb_posts_url = data.get("paging", {}).get("next") if fetched_posts < max_posts else None

        # 6. Final Calculations
        insight_metrics, recommendations = compute_insight_metrics(insights)

        return cors_json_response({
            "profile": profile_data,
            "insights": insights,
            "insightMetrics": insight_metrics,
            "recommendations": recommendations
        })

    except Exception as e:
        logger.error(f"SYSTEM CRASH: {str(e)}")
        return cors_json_response({
            "error": "Internal Server Error",
            "details": str(e)
        }, status=500)
    
@csrf_exempt
def request_report(request):
    from .tasks import generate_report  # move import here

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    token = data.get("token")
    method = data.get("method", "ml")
    max_posts = int(data.get("max_posts", 5))

    if not token:
        return JsonResponse({"error": "Token required"}, status=400)

    report_id = str(uuid.uuid4())
    generate_report.delay(report_id, token, method, max_posts, user_id=request.user.id)

    return JsonResponse({"report_id": report_id, "status": "pending"})

@csrf_exempt
def get_reports(request):
    user_id = str(request.user.id)
    profile_id = request.GET.get("profile_id")

    query = {}
    if profile_id:
        query["profile_id"] = profile_id

    reports = list(reports_collection.find(query).sort("created_at", -1))

    for r in reports:
        r["_id"] = str(r["_id"])
    return JsonResponse({"reports": reports})

@csrf_exempt
def get_report(request, report_id):
    report = reports_collection.find_one({"report_id": report_id, "user_id": str(request.user.id)})
    if not report:
        return JsonResponse({"error": "Report not found"}, status=404)
    report["_id"] = str(report["_id"])
    return JsonResponse(report)