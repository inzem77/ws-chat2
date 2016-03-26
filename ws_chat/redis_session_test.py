import asyncio
import time
from aiohttp import web
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import aiohttp_session
import aioredis

@asyncio.coroutine
def handler(request):
    session = yield from get_session(request)
    session['last_visit'] = time.time()
    return web.Response(body=b'OK')

@asyncio.coroutine
def init(loop):
    redis = yield from aioredis.create_pool(('localhost', 6379), loop=loop)
    storage = aiohttp_session.redis_storage.RedisStorage(redis)
    session_middleware = aiohttp_session.session_middleware(storage)

    app = aiohttp.web.Application(middlewares=[session_middleware])
    app.router.add_route('GET', '/', handler)
    srv = yield from loop.create_server(
        app.make_handler(), '0.0.0.0', 8081)
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass


