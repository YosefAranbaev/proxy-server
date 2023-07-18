import aiohttp
from aiohttp import web
from proxy_cache import get_cached_response, cache_response
from utils.utils import check_request_rate_limits, get_page_number
cache = {}

async def forward_request(request):
    # Check if the request rate exceeds the limits
    if not check_request_rate_limits(request):
        return web.Response(text='Rate limit exceeded', status=429)
    page = get_page_number(request)
    # Check if the request is already cached
    cached_response = get_cached_response(request, page)
    if cached_response:
        return web.Response(text=cached_response, content_type='application/json')
    
    # Forward the request to the remote server
    async with aiohttp.ClientSession() as session:
        url = f'https://reqres.in/api/users?page={page}'
        async with session.request(method=request.method, url=url) as response:
            assert response.status == 200
            response_text = await response.text()
            
            # Cache the response for future use
            cache_response(request, response_text, page)
            
            return web.Response(text=response_text, content_type='application/json')
        
