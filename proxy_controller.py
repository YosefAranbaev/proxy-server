import aiohttp
import time
from aiohttp import web
from proxy_cache import get_cached_response, cache_response
from constants import REQUESTS_PER_MINUTE_LIMIT, REQUESTS_PER_DAY_LIMIT

cache = {}

def get_page_number(request):
    query_params = request.query

    if 'page' in query_params:
        try:
            page_number = int(query_params['page'])
            return page_number
        except ValueError:
            raise web.HTTPBadRequest(text="Invalid page number")

    raise web.HTTPBadRequest(text="Page number not specified")


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

def check_request_rate_limits(request):
    # Check if it is a new day and reset rate limits if necessary
    reset_rate_limits_if_new_day(request)
    
    # Track requests per minute using a sliding window
    current_time = int(time.time())
    window_start_time = current_time - 60  # 60 seconds in a minute
    request_timestamps = [timestamp for timestamp in request.app['request_timestamps']
                          if timestamp >= window_start_time]
    
    if len(request_timestamps) >= REQUESTS_PER_MINUTE_LIMIT:
        return False
    
    # Track requests per day using a counter
    request_counter = request.app['request_counter']
    if request_counter >= REQUESTS_PER_DAY_LIMIT:
        return False
    
    # Update the request rate tracking data
    request.app['request_timestamps'] = request_timestamps
    request.app['request_timestamps'].append(current_time)
    request.app['request_counter'] += 1    
    return True

def reset_rate_limits_if_new_day(request):
    current_time = int(time.time())
    if current_time >= request.app['reset_time']:
        request.app['request_timestamps'] = []
        request.app['request_counter'] = 0
        reset_time = (current_time // 86400 + 1) * 86400  # Next day reset time
        request.app['reset_time'] = reset_time
