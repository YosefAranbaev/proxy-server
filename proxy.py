import asyncio
from aiohttp import web
from proxy_router import setup_routes

async def start_server():
    app = web.Application()
    app['request_timestamps'] = []
    app['request_counter'] = 0
    app['reset_time'] = 0
    setup_routes(app)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print("Proxy server started at http://localhost:8080")

# Run the proxy server
loop = asyncio.get_event_loop()
loop.create_task(start_server())

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()
