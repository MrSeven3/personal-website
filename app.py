from werkzeug.exceptions import HTTPException
from flask import Flask, render_template, abort
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv
from markdown_it import MarkdownIt
import blog_utils
import cache_utils
import sentry_sdk
import os
import linkify_it

load_dotenv()

md = MarkdownIt("gfm-like2")
sentry_sdk.init(os.environ.get("SENTRY_DSN"), integrations=[FlaskIntegration()])
app = Flask(__name__)

@app.route("/")
def da_main_page():
    website_uptime = cache_utils.get_website_uptime()
    docker_data = cache_utils.get_docker_data()

    return render_template("index.html",
                           docker_services=docker_data[0],
                           docker_containers=docker_data[1],
                           uptime=website_uptime
    )

@app.route("/blogs")
@app.route("/blogs/")
def blog_list():
    blogs = blog_utils.get_blog_previews()

    final_list = ""
    for blog in blogs:
        final_list += '<div class="blog-list-entry space-grotesk-normal"><a href="/blogs/'+blog[1]+'"><h2 class="space-grotesk-header text-highlight">'+blog[0]+'</h2></a><p>'+blog[2]+'</p></div>\n'
    return render_template("/blog/blog_list.html", blog_list=final_list)

@app.route("/blogs/<slug>")
def blog_entry(slug):
    blog_info = blog_utils.get_blog_info(slug)
    if blog_info is None:
        abort(404)

    return render_template("/blog/blog_template.html",
                           blog_title=blog_info[1],
                           blog_html=md.render(blog_info[5])
   )



@app.errorhandler(HTTPException)
def fancy_error(error):
    return render_template("error.html",
                           http_code=error.code,
                           http_meaning=error.name,
                           error=error.description
   ), error.code
