from werkzeug.exceptions import HTTPException
from flask import Blueprint, render_template
import utils.cache

main_routes = Blueprint("main", __name__)

@main_routes.route("/")
def da_main_page():
    website_uptime = utils.cache.get_website_uptime()
    docker_data = utils.cache.get_docker_data()
    return render_template("index.html",
                           docker_services=docker_data[0],
                           docker_containers=docker_data[1],
                           uptime=website_uptime
    )

@main_routes.app_errorhandler(HTTPException)
def fancy_error(error):
    return render_template("error.html",
                           http_code=error.code,
                           http_meaning=error.name,
                           error=error.description
    ), error.code