from flask import Blueprint, redirect, request, abort, session, render_template
import requests
import secrets
import os, shutil
import urllib.parse

admin_routes = Blueprint("admin", __name__, url_prefix="/admin")

@admin_routes.route("/login")
def sso_login_path():
    if session.get('logged_in'):
        return redirect("/admin")

    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state

    oauth_redirect_url = "https://" + os.environ.get("OAUTH_DOMAIN") + "/oidc/auth?client_id="+os.environ.get("OAUTH_CLIENT_ID")+"&redirect_uri="+os.environ.get("OAUTH_REDIRECT_URI")+"&response_type=code&scope=openid&state="+str(state)

    return redirect(oauth_redirect_url)

@admin_routes.route("/login/oauth")
def handle_oauth():
    if session.get('logged_in'):
        return redirect("/admin")

    error = request.args.get("error")
    if error == "access_denied": abort(403)
    elif error: abort(500)

    if request.args.get("state") != session.pop("oauth_state", None):
        abort(401)

    exchange_code = request.args.get("code")

    #validate that the auth code is real by exchanging for a token
    token_request_payload = {
        "client_id": str(os.environ.get("OAUTH_CLIENT_ID")),
        "client_secret": str(os.environ.get("OAUTH_CLIENT_SECRET")),
        "redirect_uri": str(os.environ.get("OAUTH_REDIRECT_URI")),
        "code": str(exchange_code),
        "grant_type": "authorization_code"
    }

    response = requests.post("https://" + os.environ.get("OAUTH_DOMAIN") + "/oidc/token",data=token_request_payload)
    error = response.json().get("error")
    if error == "invalid_grant": abort(403)
    elif error: abort(500)

    session["logged_in"] = True

    return redirect("/admin")

@admin_routes.route("/")
def most_basic_landing_page_ever_because_only_i_will_see_it():
    if not session.get('logged_in'):
        return redirect("/admin/login")

    return render_template("admin/landing.html")

@admin_routes.route("/clear-sessions")
def clear_all_sessions():
    if not session.get('logged_in'):
        print("user isnt logged in, redirecting")
        return redirect("/admin/login")

    shutil.rmtree("flask_session")
    os.mkdir("flask_session")
    session.clear()

    return redirect("/")

@admin_routes.route("/well-known-config", methods=['GET','POST'])
def dynamic_well_known_config():
    import well_known_utils
    if request.method == "GET":
        return render_template("admin/well-known-config.html")

    slug = request.form['slug']
    content = request.form['content']
    domain = request.form['domain']

    well_known_utils.add_well_known_entry(slug,content,domain)

    return redirect("/admin/well-known-config")