import time
import uuid
import json
import logging
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# We avoid ThreadPoolExecutor on Render Free Tier to prevent Memory (OOM) crashes
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

# CONFIG FOR STABILITY
REQUEST_DELAY = 0.2
MAX_POSTS_LIMIT = 10  # Reduced for free-tier performance
MAX_COMMENTS_LIMIT = 5

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

# ===================================
# MAIN ANALYSIS VIEW
# ===================================
@csrf_exempt
def analyze_facebook(request):
    # 1. Handle Preflight OPTIONS request
    if request.method == "OPTIONS":
        return cors_json_response({})

    if request.method != "GET":
        return cors_json_response({"error": "Method not allowed"}, status=405)

    try:
        # 2. Token extraction
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        
        token = token or request.GET.get("token") or request.COOKIES.get("fb_token")

        if not token:
            return cors_json_response({"error": "Authorization token missing"}, status=401)

        method = request.GET.get("method", "ml")
        
        # 3. Fetch Profile
        profile_url = (
            f"https://graph.facebook.com/v19.0/me?"
            f"fields=id,name,birthday,gender,picture.width(200).height(200)"
            f"&access_token={token}"
        )
        profile_res = requests.get(profile_url, timeout=10)
        if profile_res.status_code != 200:
            return cors_json_response({"error": "Invalid Facebook token"}, status=401)
        profile_data = profile_res.json()

        # 4. Fetch Posts
        insights = []
        fetched_posts = 0
        fb_posts_url = (
            f"https://graph.facebook.com/v19.0/me/posts?"
            f"fields=message,story,status_type,created_time,object_id&limit=5&access_token={token}"
        )

        while fb_posts_url and fetched_posts < MAX_POSTS_LIMIT:
            res = requests.get(fb_posts_url, timeout=10)
            if res.status_code != 200: break
            
            data = res.json()
            posts = data.get("data", [])

            for post in posts:
                if fetched_posts >= MAX_POSTS_LIMIT: break
                
                content = post.get("message") or post.get("story") or ""
                
                # Analyze Post
                try:
                    analysis = analyze_text(content, method)
                except Exception as e:
                    logger.error(f"Post analysis failed: {e}")
                    analysis = {"original": content, "label": "neutral"}

                analysis.update({
                    "timestamp": post.get("created_time"),
                    "is_respectful": is_respectful(content),
                    "mentions_location": mentions_location(content),
                    "privacy_disclosure": discloses_personal_info(content),
                    "toxic": is_toxic(content),
                    "type": "post"
                })
                insights.append(analysis)

                # 5. Fetch and Analyze Comments (Serial loop to save RAM)
                comment_url = f"https://graph.facebook.com/v19.0/{post['id']}/comments?limit={MAX_COMMENTS_LIMIT}&access_token={token}"
                c_res = requests.get(comment_url, timeout=5)
                if c_res.status_code == 200:
                    comments_data = c_res.json().get("data", [])
                    for c in comments_data:
                        c_text = c.get("message", "")
                        try:
                            c_analysis = analyze_text(c_text, method)
                        except:
                            c_analysis = {"original": c_text, "label": "neutral"}
                        
                        c_analysis.update({
                            "timestamp": c.get("created_time"),
                            "is_respectful": is_respectful(c_text),
                            "type": "comment"
                        })
                        insights.append(c_analysis)
                
                fetched_posts += 1
                time.sleep(REQUEST_DELAY) # Rate limiting respect

            fb_posts_url = data.get("paging", {}).get("next") if fetched_posts < MAX_POSTS_LIMIT else None

        # 6. Final Metrics
        insight_metrics, recommendations = compute_insight_metrics(insights)

        return cors_json_response({
            "profile": profile_data,
            "insights": insights,
            "insightMetrics": insight_metrics,
            "recommendations": recommendations
        })

    except Exception as e:
        logger.error(f"CRITICAL SYSTEM ERROR: {str(e)}")
        return cors_json_response({
            "error": "Internal Server Error",
            "details": str(e)
        }, status=500)

# ===================================
# BACKGROUND TASKS / REPORTS
# ===================================
@csrf_exempt
def request_report(request):
    if request.method == "OPTIONS": return cors_json_response({})
    try:
        data = json.loads(request.body)
        token = data.get("token")
        if not token: return cors_json_response({"error": "Token required"}, 400)
        
        report_id = str(uuid.uuid4())
        # Note: Ensure Celery is configured if using .delay()
        from .tasks import generate_report
        generate_report.delay(report_id, token, data.get("method", "ml"), 50, "guest")
        
        return cors_json_response({"report_id": report_id, "status": "pending"})
    except Exception as e:
        return cors_json_response({"error": str(e)}, 500)