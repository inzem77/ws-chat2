import asyncio
import time
from aiohttp import web
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aioredis import create_pool
from aiohttp_session import redis_storage, session_middleware
import random

@asyncio.coroutine
def handler(request):
    session = yield from get_session(request)
    session['last_visit'] = time.time()
    return web.Response(body=b'OK')

@asyncio.coroutine
def init(loop):
    redis = yield from create_pool(('localhost', 6379))
    storage = redis_storage.RedisStorage(redis)
    session_middleware1 = session_middleware(storage)
    app = web.Application(middlewares=[session_middleware1])
    #app = web.Application(middlewares=[session_middleware(
    #    EncryptedCookieStorage(b'Thirty  two  length  bytes  key.'))])
    app.router.add_route('GET', '/', handler)
    srv = yield from loop.create_server(
        app.make_handler(), '0.0.0.0', 8081)
    return srv
"""
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
"""
dsn = 'dbname=ws_chat user=ws_chat password=ws_chat host=localhost port=5432'


from aiopg.pool import create_pool

@asyncio.coroutine
def test_select():
    pool = yield from create_pool(dsn)

    with (yield from pool) as conn:
        cur = yield from conn.cursor()
        #id = await cur.execute("select nextval('chat_messages_id_seq'::regclass)")
        #print(id)
        yield from cur.execute("insert into chat_messages(id, message, session_key, admin_user_id) "
                               "values ({}, 'test', '12345678901234561234567890123456', 1 )".format(random.randint(1,100000)))
        #ret = yield from cur.fetchone()
        #assert ret == (1,), ret


asyncio.get_event_loop().run_until_complete(test_select())