import requests
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse
from urllib.parse import urlencode

FACEBOOK_CLIENT_ID = settings.FB_APP_ID
FACEBOOK_CLIENT_SECRET = settings.FB_APP_SECRET
FRONTEND_URL = getattr(settings, "FRONTEND_URL", "http://localhost:3000")  # React frontend

def facebook_login(request):
    fb_auth_url = "https://www.facebook.com/v15.0/dialog/oauth"
    params = {
        "client_id": FACEBOOK_CLIENT_ID,
        "redirect_uri": f"{settings.BASE_URL}/auth/facebook/callback/",
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
        "redirect_uri": f"{settings.BASE_URL}/auth/facebook/callback/",
        "client_secret": FACEBOOK_CLIENT_SECRET,
        "code": code,
    }
    r = requests.get(token_url, params=params)
    if r.status_code != 200:
        return HttpResponse("Failed to get access token", status=400)

    access_token = r.json().get("access_token")
    if not access_token:
        return HttpResponse("Access token not found", status=400)

    # Set the token as a cookie so React can read it
    response = redirect(f"{FRONTEND_URL}/dashboard")
    response.set_cookie("fb_token", access_token, httponly=False, max_age=3600*24*7)  # 7 days
    return response
