from flask import Blueprint, redirect, request, abort
import os

admin_routes = Blueprint("admin", __name__, url_prefix="/admin")

@admin_routes.route("login")
def sso_login_path():
    oauth_redirect_url = "https://" + os.environ.get("OAUTH_DOMAIN") + "/oidc/auth?client_id="+os.environ.get("OAUTH_CLIENT_ID")+"&client_secret="+os.environ.get("OAUTH_CLIENT_SECRET")+"&redirect_uri="+os.environ.get("OAUTH_REDIRECT_URI")+"&response_type=code"
    return redirect(oauth_redirect_url)

@admin_routes.route("login/oauth")
def handle_oauth():

    error = request.args.get("error")
    if error == "access_denied": abort(403)
    elif error: abort(500)


    authorization_code = request.args.get("AUTHORIZATION_CODE")
    print(authorization_code)

    print(str(request.args))
    return 200