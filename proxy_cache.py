import time

# Define the cache duration in minutes
CACHE_DURATION_MINUTES = 5
cache = {}

def get_cached_response(request):
    cache_key = request.path_qs
    if cache_key in cache:
        cache_entry = cache[cache_key]
        print(cache_entry['expiration_time'])
        if cache_entry['expiration_time'] >= time.time():
            return cache_entry['response']
        else:
            del cache[cache_key]
    
    return None

def cache_response(request, response_text):
    cache_key = request.path_qs
    cache[cache_key] = {
        'response': response_text,
        'expiration_time': time.time() + CACHE_DURATION_MINUTES * 60
    }
