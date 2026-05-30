from werkzeug.exceptions import HTTPException
from flask import Flask, render_template
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv
import mysql_utils
import sentry_sdk
import os

load_dotenv()


sentry_sdk.init(os.environ.get("SENTRY_DSN"), integrations=[FlaskIntegration()])
app = Flask(__name__)

@app.route("/")
def da_main_page():
    website_uptime = mysql_utils.get_website_uptime()
    docker_data = mysql_utils.get_docker_data()

    return render_template("index.html",
                           docker_services=docker_data[0],
                           docker_containers=docker_data[1],
                           uptime=website_uptime
    )

@app.errorhandler(HTTPException)
def fancy_error(error):
    return render_template("error.html",
                           http_code=error.code,
                           http_meaning=error.name,
                           error=error.description
   ), error.code
