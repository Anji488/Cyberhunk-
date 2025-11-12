import requests
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse
from urllib.parse import urlencode

FACEBOOK_CLIENT_ID = settings.FB_APP_ID
FACEBOOK_CLIENT_SECRET = settings.FB_APP_SECRET
BASE_URL = settings.BASE_URL  # e.g. https://spurtive-subtilely-earl.ngrok-free.dev
FRONTEND_URL = settings.FRONTEND_URL  # e.g. http://localhost:5173 or your deployed React site


def facebook_login(request):
    fb_auth_url = "https://www.facebook.com/v15.0/dialog/oauth"
    params = {
        "client_id": FACEBOOK_CLIENT_ID,
        "redirect_uri": f"{BASE_URL}/auth/facebook/callback/",
        "scope": "email,public_profile,user_posts",
        "response_type": "code",
    }
    url = f"{fb_auth_url}?{urlencode(params)}"
    return redirect(url)


def facebook_callback(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Missing code in callback", status=400)

    # Exchange code for access token
    token_url = "https://graph.facebook.com/v15.0/oauth/access_token"
    params = {
        "client_id": FACEBOOK_CLIENT_ID,
        "redirect_uri": f"{BASE_URL}/auth/facebook/callback/",
        "client_secret": FACEBOOK_CLIENT_SECRET,
        "code": code,
    }

    try:
        r = requests.get(token_url, params=params)
        r.raise_for_status()
        access_token = r.json().get("access_token")
        if not access_token:
            return HttpResponse("Access token not found", status=400)
    except requests.RequestException:
        return HttpResponse("Failed to get access token", status=400)

    # ✅ Redirect with token in URL (frontend will set cookie)
    return redirect(f"{FRONTEND_URL}/auth/callback?token={access_token}")
