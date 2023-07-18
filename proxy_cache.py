import time

# Define the cache duration in minutes
CACHE_DURATION_MINUTES = 5
cache = {}

def get_cached_response(request, page):
    cache_key = f"{request.path_qs}?page={page}"
    if cache_key in cache:
        cache_entry = cache[cache_key]
        print(cache_entry['expiration_time'])
        if cache_entry['expiration_time'] >= time.time():
            return cache_entry['response']
        else:
            del cache[cache_key]
    
    return None

def cache_response(request, response_text, page):
    cache_key = f"{request.path_qs}?page={page}"
    cache[cache_key] = {
        'response': response_text,
        'expiration_time': time.time() + CACHE_DURATION_MINUTES * 60
    }
