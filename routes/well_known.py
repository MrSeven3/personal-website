from flask import Blueprint, request, Response
import urllib.parse

dynamic_well_known_routes = Blueprint("dyn-well-known",__name__)

@dynamic_well_known_routes.route("/.well-known/<file>")
def serve_dynamic_well_known(file):
    domain = urllib.parse.urlsplit(request.base_url).hostname

    import well_known_utils
    contents = well_known_utils.get_well_known_entry(file,domain)
    if contents is None: return {"error":"well_known_not_found"}, 404

    return Response(contents, mimetype="text/plain")