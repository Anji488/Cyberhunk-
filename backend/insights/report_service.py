# backend/insights/report_service.py
import time
import requests
import logging

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
REQUEST_DELAY = 0.3


def analyze_facebook_data(token, method="ml", max_posts=5):
    insights = []
    fetched_posts = 0

    fb_posts_url = (
        f"https://graph.facebook.com/v19.0/me/posts?"
        f"fields=message,story,status_type,created_time,object_id"
        f"&limit=5&access_token={token}"
    )

    while fb_posts_url and fetched_posts < max_posts:
        res = requests.get(fb_posts_url, timeout=20)
        if res.status_code != 200:
            raise Exception("Facebook API failed")

        data = res.json()

        for post in data.get("data", []):
            if fetched_posts >= max_posts:
                break

            text = post.get("message") or post.get("story") or ""
            analysis = analyze_text(text, method)

            analysis.update({
                "timestamp": post.get("created_time"),
                "is_respectful": is_respectful(text),
                "mentions_location": mentions_location(text),
                "privacy_disclosure": discloses_personal_info(text),
                "toxic": is_toxic(text),
                "misinformation_risk": is_potential_misinformation(text),
                "type": "post"
            })

            insights.append(analysis)
            fetched_posts += 1
            time.sleep(REQUEST_DELAY)

        fb_posts_url = data.get("paging", {}).get("next")

    metrics, recommendations = compute_insight_metrics(insights)

    return {
        "insights": insights,
        "insightMetrics": metrics,
        "recommendations": recommendations
    }

def fetch_profile(token):
    url = (
        f"https://graph.facebook.com/v19.0/me?"
        f"fields=id,name,birthday,gender,picture.width(200).height(200)"
        f"&access_token={token}"
    )
    try:
        res = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        logger.error(f"Facebook API unreachable: {e}")
        return None

    return res.json() if res.status_code == 200 else None
