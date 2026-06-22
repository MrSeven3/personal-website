from flask import Blueprint, render_template, abort
from markdown_it import MarkdownIt
import utils.blog

blog_routes = Blueprint("blog", __name__, url_prefix="/blogs")
md = MarkdownIt("gfm-like2")

@blog_routes.route("/")
@blog_routes.route("")
def blog_list():
    blogs = utils.blog.get_blog_previews()

    final_list = ""
    for blog in blogs:
        final_list += '<div class="blog-list-entry space-grotesk-normal"><a href="/blogs/'+blog[1]+'"><h2 class="space-grotesk-header text-highlight">'+blog[0]+'</h2></a><p>'+blog[2]+'</p></div>\n'

    return render_template("/blog/blog-list.html", blog_list=final_list)

@blog_routes.route("/<slug>")
def blog_entry(slug):
    blog_info = utils.blog.get_blog_info(slug)

    if blog_info is None:
        abort(404)
    return render_template("/blog/blog-template.html",
                           blog_title=blog_info[1],
                           blog_html=md.render(blog_info[5].decode())
   )