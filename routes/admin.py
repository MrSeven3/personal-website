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
    if response.status_code != 200: abort(500)
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
    if not session.get('logged_in'):
        print("user isnt logged in, redirecting")
        return redirect("/admin/login")

    import well_known_utils
    if request.method == "GET":
        entry_list = well_known_utils.get_all_well_known_entries()
        if entry_list is None: return render_template("admin/well-known-config.html")

        entry_list_html = ""
        for entry in entry_list:
            entry_list_html += '<div><p style="white-space-collapse: preserve-spaces; margin: 0 auto;">slug: '+entry[1]+'        domain: '+entry[3]+'</p><p style="margin: 0 auto;">content: '+entry[2]+'</p></div>'

        return render_template("admin/well-known-config.html",entry_list=entry_list_html)

    slug = request.form.get('slug')
    content = request.form.get('content')
    domain = request.form.get('domain')

    if slug is None or content is None or domain is None or slug == "" or content == "" or domain == "":
        abort(400)

    well_known_utils.add_well_known_entry(slug,content,domain)

    return redirect("/admin/well-known-config")

@admin_routes.route("/well-known-config/remove-well-known-entry",methods=['POST'])
def remove_well_known_config():
    if not session.get('logged_in'):
        print("user isnt logged in, redirecting")
        return redirect("/admin/login")

    import well_known_utils

    slug = request.form.get('slug')
    domain = request.form.get('domain')

    if slug is None or domain is None or slug == "" or domain == "":
        abort(400)

    well_known_utils.delete_well_known_entry(slug,domain)

    return redirect("/admin/well-known-config")