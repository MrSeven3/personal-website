from flask import Blueprint, redirect
import os

admin_routes = Blueprint("admin", __name__, url_prefix="/admin")

@admin_routes.route("login")
def sso_login_path():
    oauth_redirect_url = "https://" + os.environ.get("OAUTH_DOMAIN") + "/oidc/auth"
    return redirect(oauth_redirect_url)

@admin_routes.route("login/oauth")
def handle_oauth():
    oauth_client_id = os.environ.get("OAUTH_CLIENT_ID")
    oauth_client_secret = os.environ.get("OAUTH_CLIENT_SECRET")