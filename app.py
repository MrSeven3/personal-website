from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_session import Session
from dotenv import load_dotenv
from utils.setup import init_db
from apscheduler.schedulers.background import BackgroundScheduler
import sentry_sdk
import os

init_db()
load_dotenv()
sentry_sdk.init(os.environ.get("SENTRY_DSN"), integrations=[FlaskIntegration()])

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

app.config["SESSION_TYPE"] = "filesystem"
Session(app)

scheduler = BackgroundScheduler()
scheduler.start()

import utils.cache
scheduler.add_job(
    func=utils.cache.fetch_docker_data,
    id="docker_data_refresh",
    trigger="interval",
    minutes=5
)
scheduler.add_job(
    func=utils.cache.fetch_website_uptime,
    id="uptime_data_refresh",
    trigger="interval",
    minutes=15
)

from routes.main import main_routes
from routes.blog import blog_routes
from routes.admin import admin_routes
from routes.well_known import dynamic_well_known_routes

app.register_blueprint(main_routes)
app.register_blueprint(blog_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(dynamic_well_known_routes)

