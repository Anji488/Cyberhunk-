import time
import requests
import logging
import uuid
import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Import MongoDB collection
from .mongo_client import reports_collection

# Import analysis services
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

# --- CONSTANTS ---
MAX_THREADS = 5
REQUEST_DELAY = 0.3
DEFAULT_MAX_POSTS = 10
MAX_POSTS_LIMIT = 20
MAX_COMMENTS_LIMIT = 5
MAX_NESTED = 5

# -----------------------------
# Helper functions
# -----------------------------
def safe_request(url: str) -> dict:
    time.sleep(REQUEST_DELAY)
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
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

# ===================================
# CORS SAFE JSON RESPONSE HELPER
# ===================================
def cors_json_response(data, status=200):
    """Ensures CORS headers are present even if the view catches an error."""
    response = JsonResponse(data, status=status)
    response["Access-Control-Allow-Origin"] = "https://cyberhunk.vercel.app"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# -----------------------------
# Main Analysis View (With DB Save)
# -----------------------------
@csrf_exempt
def analyze_facebook(request):
    if request.method == "OPTIONS":
        return cors_json_response({})

    if request.method != "GET":
        return cors_json_response({"error": "Method not allowed"}, status=405)

    try:
        # 1. Token Extraction
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        
        token = token or request.GET.get("token") or request.COOKIES.get("fb_token")

        if not token:
            return cors_json_response({"error": "Authorization token missing"}, status=401)

        method = request.GET.get("method", "ml")
        max_posts = min(int(request.GET.get("max_posts", DEFAULT_MAX_POSTS)), MAX_POSTS_LIMIT)

        # 2. Fetch Profile
        profile_data = fetch_profile(token)
        if not profile_data or "id" not in profile_data:
            return cors_json_response({"error": "Facebook rejected token or it expired"}, status=401)

        # 3. Main Loop
        insights = []
        shared_cache = {}
        fetched_posts = 0
        fb_posts_url = (
            f"https://graph.facebook.com/v19.0/me/posts?"
            f"fields=message,story,status_type,created_time,object_id&limit=5&access_token={token}"
        )

        while fb_posts_url and fetched_posts < max_posts:
            res = requests.get(fb_posts_url, timeout=10)
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
                        shared_res = requests.get(
                            f"https://graph.facebook.com/v19.0/{shared_id}?fields=message&access_token={token}",
                            timeout=5
                        )
                        if shared_res.status_code == 200:
                            shared_cache[shared_id] = shared_res.json().get("message", "")
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

                # 4. Fetch & Analyze Comments
                comment_url = (
                    f"https://graph.facebook.com/v19.0/{post['id']}/comments?"
                    f"fields=message,created_time&limit={MAX_COMMENTS_LIMIT}&access_token={token}"
                )
                c_res = requests.get(comment_url, timeout=5)
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

        # 5. Final Calculations
        insight_metrics, recommendations = compute_insight_metrics(insights)

        # -----------------------------
        # 💾 SAVE TO MONGODB
        # -----------------------------
        try:
            report_doc = {
                "report_id": str(uuid.uuid4()),
                "user_id": str(request.user.id) if request.user.is_authenticated else "anonymous",
                "profile": profile_data,
                "insights": insights,
                "insightMetrics": insight_metrics,
                "recommendations": recommendations,
                "method": method,
                "created_at": datetime.utcnow()
            }
            reports_collection.insert_one(report_doc)
            logger.info(f"Report saved to MongoDB: {report_doc['report_id']}")
        except Exception as e:
            logger.error(f"Database save failed: {e}")

        # 6. Return response
        return cors_json_response({
            "profile": profile_data,
            "insights": insights,
            "insightMetrics": insight_metrics,
            "recommendations": recommendations
        })

    except Exception as e:
        logger.error(f"SYSTEM CRASH: {str(e)}")
        return cors_json_response({"error": "Internal Server Error", "details": str(e)}, status=500)

# -----------------------------
# Async Reporting Views
# -----------------------------
@csrf_exempt
@login_required
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