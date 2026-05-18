from flask import Flask, render_template
import mysql_utils

app = Flask(__name__)

@app.route("/")
def da_main_page():
    website_uptime = mysql_utils.get_website_uptime()
    docker_data = mysql_utils.get_docker_data()

    return render_template("index.html", docker_services=docker_data[0],docker_containers=docker_data[1], uptime=website_uptime)
