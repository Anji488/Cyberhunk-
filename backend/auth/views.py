import requests
import secrets
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


FACEBOOK_CLIENT_ID = settings.FB_APP_ID
FACEBOOK_CLIENT_SECRET = settings.FB_APP_SECRET
BASE_URL = settings.BASE_URL
FRONTEND_URL = settings.FRONTEND_URL

REDIRECT_URI = f"{BASE_URL}/auth/facebook/callback/"

def facebook_login(request):
    """Redirect user to Facebook OAuth login page."""
    state = secrets.token_urlsafe(16)
    request.session["fb_oauth_state"] = state

    fb_auth_url = "https://www.facebook.com/v15.0/dialog/oauth"
    params = {
        "client_id": FACEBOOK_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "email,public_profile,user_posts",
        "response_type": "code",
        "state": state,
    }

    url = f"{fb_auth_url}?{requests.compat.urlencode(params)}"
    return redirect(url)



@csrf_exempt
def facebook_callback(request):
    """Handle Facebook callback and redirect to frontend with token."""
    code = request.GET.get("code")
    state = request.GET.get("state")

    if not code:
        return HttpResponse("Missing code in callback", status=400)

    if state != request.session.get("fb_oauth_state"):
        return HttpResponse("Invalid OAuth state", status=400)

    token_url = "https://graph.facebook.com/v15.0/oauth/access_token"
    params = {
        "client_id": FACEBOOK_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "client_secret": FACEBOOK_CLIENT_SECRET,
        "code": code,
    }

    try:
        r = requests.get(token_url, params=params)
        r.raise_for_status()
        access_token = r.json().get("access_token")

        if not access_token:
            return HttpResponse("Access token not found", status=400)

    except requests.RequestException as e:
        return HttpResponse(f"Failed to get access token: {e}", status=400)

    return redirect(f"{FRONTEND_URL}/auth/callback?token={access_token}")
