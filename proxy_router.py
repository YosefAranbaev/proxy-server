from aiohttp import web
from proxy_controller import forward_request

def setup_routes(app):
    app.router.add_route('GET', '/listusers', forward_request)
