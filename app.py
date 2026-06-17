from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv
import sentry_sdk
import os



load_dotenv()
sentry_sdk.init(os.environ.get("SENTRY_DSN"), integrations=[FlaskIntegration()])
app = Flask(__name__)

from routes.main import main_routes
from routes.blog import blog_routes
from routes.admin import admin_routes

app.register_blueprint(main_routes)
app.register_blueprint(blog_routes)
app.register_blueprint(admin_routes)
