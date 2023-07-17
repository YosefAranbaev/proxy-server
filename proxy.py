import aiohttp
import asyncio
from aiohttp import web
import time

# Define the rate limiting parameters
REQUESTS_PER_MINUTE_LIMIT = 10
REQUESTS_PER_DAY_LIMIT = 1000

# Define the cache duration in minutes
CACHE_DURATION_MINUTES = 1
cache = {}

async def forward_request(request):
    # Check if the request rate exceeds the limits
    if not check_request_rate_limits(request):
        return web.Response(text='Rate limit exceeded', status=429)
    
    # Check if the request is already cached
    cached_response = get_cached_response(request)
    print("--->",cached_response)
    if cached_response:
        return web.Response(text=cached_response, content_type='application/json')
    
    # Forward the request to the remote server
    async with aiohttp.ClientSession() as session:
        async with session.request(method=request.method, url='https://reqres.in/api/users?page=2') as response:
            assert response.status == 200
            response_text = await response.text()
            
            # Cache the response for future use
            cache_response(request, response_text)
            
            return web.Response(text=response_text, content_type='application/json')

def check_request_rate_limits(request):
    # Track requests per minute using a sliding window
    current_time = int(time.time())
    minute_window_start_time = current_time - 60  # 60 seconds in a minute
    minute_request_timestamps = [timestamp for timestamp in request.app['request_timestamps']
                          if timestamp >= minute_window_start_time]
    
    if len(minute_request_timestamps) >= REQUESTS_PER_MINUTE_LIMIT:
        return False
    
    day_window_start_time = current_time - 86400  # 86400 seconds in a day
    day_request_timestamps = [timestamp for timestamp in request.app['request_timestamps']
                          if timestamp >= day_window_start_time]
    
    if len(day_request_timestamps) >= REQUESTS_PER_DAY_LIMIT:
        return False
    
    # Update the request rate tracking data
    request.app['request_timestamps'] = day_request_timestamps
    request.app['request_timestamps'].append(current_time)
    print(request.app['request_timestamps'])
    return True


def get_cached_response(request):
    cache_key = request.path_qs
    
    if cache_key in cache:
        cache_entry = cache[cache_key]
        if cache_entry['expiration_time'] >= time.time():
            return cache_entry['response']
        else:
            del cache[cache_key]
    
    return None

def cache_response(request, response_text):
    cache_key = request.path_qs
    print(cache_key)
    cache[cache_key] = {
        'response': response_text,
        'expiration_time': time.time() + CACHE_DURATION_MINUTES * 60
    }

async def start_server():
    app = web.Application()
    app['request_timestamps'] = []
    app['reset_time'] = 0
    app.router.add_route('*', '/{path:.*}', forward_request)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

# Run the proxy server
loop = asyncio.get_event_loop()
loop.create_task(start_server())
print("Proxy server started at http://localhost:8080")

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()
