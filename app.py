from flask import Flask, render_template
import mysql_utils

app = Flask(__name__)

@app.route("/")
def da_main_page():
    website_uptime = mysql_utils.get_website_uptime()
    docker_services_online = mysql_utils.get_docker_services()

    return render_template("index.html", docker_services=docker_services_online, uptime=website_uptime)
