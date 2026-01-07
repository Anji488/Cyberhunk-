import requests
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from django.http import HttpResponse

FACEBOOK_CLIENT_ID = settings.FB_APP_ID
FACEBOOK_CLIENT_SECRET = settings.FB_APP_SECRET
BASE_URL = settings.BASE_URL
FRONTEND_URL = settings.FRONTEND_URL
REDIRECT_URI = f"{BASE_URL}/auth/facebook/callback/"

def get_facebook_user(access_token):
    """Fetch user profile from Facebook"""
    url = "https://graph.facebook.com/me"
    params = {
        "fields": "id,name,email",
        "access_token": access_token
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()


def facebook_callback(request):
    """Handle Facebook callback and login any Facebook user"""
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Missing code", status=400)

    # Exchange code for access token
    token_url = "https://graph.facebook.com/v15.0/oauth/access_token"
    params = {
        "client_id": FACEBOOK_CLIENT_ID,
        "client_secret": FACEBOOK_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }

    try:
        r = requests.get(token_url, params=params)
        r.raise_for_status()
        access_token = r.json().get("access_token")
        if not access_token:
            return HttpResponse("Failed to get access token", status=400)
    except requests.RequestException as e:
        return HttpResponse(f"Error getting token: {e}", status=400)

    # Get Facebook user info
    try:
        fb_user = get_facebook_user(access_token)
    except requests.RequestException as e:
        return HttpResponse(f"Failed to get FB user info: {e}", status=400)

    email = fb_user.get("email")
    if not email:
        return HttpResponse("Email permission is required", status=400)

    # Create or fetch Django user dynamically (ANY Facebook user can log in)
    user, _ = User.objects.get_or_create(
        username=email,
        defaults={"email": email, "first_name": fb_user.get("name", "")},
    )

    # Log in the user
    login(request, user)

    # Create or get backend token (DRF Token Auth)
    token, _ = Token.objects.get_or_create(user=user)

    # Redirect to frontend with your own token (not Facebook token)
    return redirect(f"{FRONTEND_URL}/auth/callback?token={token.key}")
