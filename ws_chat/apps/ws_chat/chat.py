import asyncio
import json
import time
import os

import aiohttp
import asyncio
import aiopg
from aiohttp import web
from aiohttp_session import get_session, session_middleware, SimpleCookieStorage, redis_storage, session_middleware
#from aiohttp_session.cookie_storage import EncryptedCookieStorage
import aioredis
import aiohttp_jinja2
import jinja2
import random
from datetime import datetime as DT

queues = []
history = {}
channels = []
app = None


loop = asyncio.get_event_loop()
dsn = 'dbname=ws_chat user=ws_chat password=ws_chat host=localhost port=5432'
dbpool = None

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *args: os.path.join(ROOT, *args)

from aiopg.connection import TIMEOUT
from aiopg.log import logger
"""
@asyncio.coroutine
def my_create_pool(dsn=None, *, minsize=10, maxsize=10,
                loop=None, timeout=TIMEOUT,
                enable_json=True, enable_hstore=True,
                echo=False,
                **kwargs):
    if loop is None:
        loop = asyncio.get_event_loop()

    pool = myDbPool(dsn, minsize, maxsize, loop, timeout,
                enable_json=enable_json, enable_hstore=enable_hstore,
                echo=echo,
                **kwargs)
    if minsize > 0:
        with (yield from pool._cond):
            yield from pool._fill_free_pool(False)
    return pool

class myDbPool(aiopg.Pool):
    async def __aenter__(self):
        logger.debug('entering context')
        conn = await self.acquire()
        return _ConnectionContextManager(self, conn)

    async def __aexit__(self, exc_type, exc, tb):
        logger.debug('exiting context')
        return self
"""

async def admin(request, host=""):
    form_data = await request.post()
    host = request.match_info.get('host', None)
    session = await get_session(request)
    session['last_visit'] = time.time()
    session['nickname'] = 'admin'
    if host:
        h = history[host] if host in history else {}
        return aiohttp_jinja2.render_template('admin.html', request, {'host': host, 'history': history})

    return aiohttp_jinja2.render_template('admin.html', request, {'history': history})

async def chat_page_admin(request):
    return aiohttp_jinja2.render_template('admin/chat.html', request, {})


@asyncio.coroutine
def sql_execute(sql, *args, **kwargs):
    with (yield from dbpool) as conn:
        cur = yield from conn.cursor()
        #await cur.execute('SELECT * from auth_user')
        #item = await cur.fetchone()
        yield from cur.execute(sql, *args, **kwargs)
        #cur.close()
        #yield from conn.close()


async def hello(request):
    global dbpool
    form_data = await request.post()
    session = await get_session(request)
    session['last_visit'] = time.time()
    host = request.host[:request.host.find(':')] # host
    if 'nickname' in form_data and form_data['nickname'] != 'admin':
        session['nickname'] = form_data['nickname']
        return web.HTTPFound(app.router['chat_page'].url(parts={'host':host})) # get chat.html

    return aiohttp_jinja2.render_template('home.html', request, {})


async def chat_page(request):
    return aiohttp_jinja2.render_template('chat.html', request, {})


async def new_msg(request):
    global loop
    session = await get_session(request)
    nickname = session['nickname']
    form_data = await request.post()
    host = request.host[:request.host.find(':')] # host
    read_task = loop.create_task(request.content.read())
    message = (await read_task).decode('utf-8')
    dt = DT.now()
    sql = """insert into chat_messages(message, session_key, admin_user_id, dt)
             values (%s, %s, 1, %s)"""
    await sql_execute(sql, (message, session.identity, dt))
    await send_message(host, nickname, message)
    return web.Response(body=b'OK')


async def send_message(host, nickname, message):
    print('{}: {}'.format(nickname, message).strip())
    if host not in history.keys():
        history[host]= {}
    if nickname not in history[host].keys():
        history[host][nickname] = []
    history[host][nickname].append('{}: {}'.format(nickname, message))
    if len(history[host][nickname]) > 20:
        del history[host][nickname][:-10]
    for queue in queues:
        await queue.put((host, nickname, message))


class WebSocketResponse(web.WebSocketResponse):
    # As of this writing, aiohttp's WebSocketResponse doesn't implement
    # "async for" yet. (Python 3.5.0 has just been releaset)
    # Let's add the protocol.
    async def __aiter__(self):
        return self

    async def __anext__(self):
        return (await self.receive())


async def websocket_handler(request):
    global loop
    host = request.host[:request.host.find(':')] # host
    session = await get_session(request)
    nickname = request.match_info.get('nickname', None)
    if not nickname:
        try:
            nickname = session['nickname']
        except:
            pass
    ws = WebSocketResponse()
    await ws.prepare(request)
    await send_message(host, 'system', 'We are connected to {} host!'.format(host))

    if host in history:
        if nickname in history[host]:
            for message in list(history[host][nickname]):
                ws.send_str(message)

    echo_task = loop.create_task(echo_loop(ws))

    async for msg in ws:
        if msg.tp == aiohttp.MsgType.close:
            print('websocket connection closed')
            break
        elif msg.tp == aiohttp.MsgType.error:
            print('ws connection closed with exception %s' % ws.exception())
            break
        else:
            print('ws connection received unknown message type %s' % msg.tp)

    await send_message(host, 'system', '{} left!'.format(nickname))
    echo_task.cancel()
    await echo_task
    return ws

async def ws_test(request):
    global loop
    host = request.host[:request.host.find(':')] # host
    ws = WebSocketResponse()
    await ws.prepare(request)
    await send_message(host, 'system', 'We are connected to {} host!'.format(host))
    ws.send_str("it's ok" + str(DT.now()))

    async for msg in ws:
        if msg.tp == aiohttp.MsgType.close:
            print('websocket connection closed')
            break
        elif msg.tp == aiohttp.MsgType.error:
            print('ws connection closed with exception %s' % ws.exception())
            break
        else:
            print('ws connection received unknown message type %s' % msg.tp)

    return ws

async def echo_loop(ws):
    queue = asyncio.Queue()
    queues.append(queue)
    try:
        while True:
            host, name, message = await queue.get()
            ws.send_str('{}: {}: {}'.format(host, name, message))
    finally:
        queues.remove(queue)

async def init(loop):
    global app, dbpool
    redis = await aioredis.create_pool(('localhost', 6379))
    storage = redis_storage.RedisStorage(redis)
    session_middleware1 = session_middleware(storage)

    #dbpool = await my_create_pool(dsn)
    dbpool = await aiopg.create_pool(dsn)

    app = web.Application(middlewares=[session_middleware1])
    #app = web.Application(middlewares=[session_middleware(
    #    EncryptedCookieStorage(b'Thirty  two  length  bytes  key.'))])
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader(path('templates')))
    # app.router.add_route('GET', '/test/ws/', ws_test)
    app.router.add_route('GET', '/admin/', admin)
    app.router.add_route('GET', '/admin/{host}/', admin)
    app.router.add_route('GET', '/admin/{host}/{nickname}/', chat_page_admin)
    app.router.add_route('POST', '/admin/{host}/{nickname}/', new_msg)
    app.router.add_route('GET', '/admin/{host}/{nickname}/ws/', websocket_handler)
    app.router.add_route('GET', '/', hello)
    app.router.add_route('POST', '/', hello)
    app.router.add_route('GET', '/{host}/', chat_page, name='chat_page')
    app.router.add_route('POST', '/{host}/', new_msg)
    app.router.add_route('GET', '/{host}/ws/', websocket_handler)

    srv = await loop.create_server(
        app.make_handler(), '0.0.0.0', 8080)
    return srv

async def end():
    await handler.finish_connections(1.0)
    srv.close()
    await srv.wait_closed()
    await app.finish()
    redis_pool.close()

#print('serving on', srv.sockets[0].getsockname())

if __name__ == "__main__":
    loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(end())
    loop.close()
