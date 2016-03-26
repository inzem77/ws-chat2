import asyncio
import time
import os, sys
import json

import aiohttp
import asyncio
import aiopg
from aiohttp_session import get_session, session_middleware, SimpleCookieStorage, redis_storage, session_middleware
import aioredis
import aiohttp_jinja2
import jinja2

import random
from datetime import datetime

from apps.ws_chat.ws_settings import *
#from apps.ws_chat import ws_settings
from apps.ws_chat.ws_utilities import *

#stream_handler = logging.StreamHandler()
#logger.addHandler(stream_handler)

# global variables of module
srv = None
redis_pool = None
"""
class NoParsingFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('parsing')

logger.addFilter(NoParsingFilter())
for i in logger.manager.loggerDict:
    if isinstance(logger.manager.loggerDict[i], logging.Logger):
        logger.manager.loggerDict[i].addFilter(NoParsingFilter())
"""
sys.path.append(ROOT)
import ws_chat

#from aiopg.connection import TIMEOUT
#from aiopg.log import logger as pg_logger

# configure django
import django
from django.conf import settings
from django.utils.importlib import import_module
from ws_chat import settings as project_settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ws_chat.settings'
django_session_engine = import_module(settings.SESSION_ENGINE)
#settings.configure(default_settings=project_settings, DEBUG=True)
#settings.configure(DEBUG=True)
django.setup()

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


def get_admin(host):
    return

async def hello(request):
    global dbpool, admins, queues_admin, queues, django_session_engine
    form_data = await request.post()
    #session = await get_session(request)
    session = await get_session(request)
    session['last_visit'] = time.time()
    host = request.host[:request.host.find(':')] # host

    #session['admin'] = get_admin(host) # it returns session key availiable admin
    if 'nickname' in form_data:
        if 'login' in form_data and 'password' in form_data :
            login = form_data['login']
            password = form_data['password']

            # check login and password from django admin as ajax query
            async with aiohttp.ClientSession() as client_session:
                async with client_session.get('http://127.0.0.1:8025/admin/') as response:
                    logger.info("Response from django is arived with status {}".format(response.status))
                    assert response.status == 200
                    csrftoken = response.cookies['csrftoken']
                    client_session.cookies['csrftoken'] = csrftoken.value # set cookie in client session
                    print("csrftoken=", csrftoken.value)

                    if response.status == 200:
                        async with client_session.post('http://127.0.0.1:8025/ajax_auth/login/', data={
                                'username': login,
                                'password': password,
                                'csrfmiddlewaretoken': csrftoken.value},
                                ) as response:
                            text = await response.text()
                            logger.debug("answer from server = {} ".format(text))
                            answer = json.loads(text)
                            if answer['success'] == True:
                                session['nickname'] = form_data['nickname']
                                session['is_admin'] = True
                                # initial queues
                                admins[host] = []
                                admins[host].append(session.identity)
                                queues_admin[session.identity] = {}
                                logger.debug(queues_admin)
                            else:
                                session['is_admin'] = False
                                return web.Response(body=b'Guest Login')

        else:

            #to = queues[session.identity]['to'] # get "to" from queues dict
            #await sql_execute(sql, (message, session.identity, dt, to))
            session_key_admin = random.choice(admins[host])
            session['nickname'] = form_data['nickname']
            session['is_admin'] = False
            # initial queues
            #queues_admin[session.identity] = Queue
            queues[session.identity] = {}
            logger.debug("queues = {} ".format(queues))
            queues[session.identity]['to'] = session_key_admin
            logger.debug(queues)

            return web.HTTPFound(app.router['chat_page'].url(parts={'host':host})) # get chat.html

    return aiohttp_jinja2.render_template('home.html', request, {})

@asyncio.coroutine
def chat_page(request):
    """
    function builds chat page with history of messages for chat's user
    """
    global redis_pool
    session = yield from get_session(request)
    session_key_admin = queues[session.identity]['to']
    sql = """select * from chat_message where
        (session_key = %s and other_session_key = %s) or
        (session_key = %s and other_session_key = %s) """
    items, description = yield from  sql_execute(sql, True, (session.identity, session_key_admin, session_key_admin, session.identity),)
    logger.info("session.identity={}, session_key_admin={}".format(session.identity, session_key_admin))
    sql_data = HandleSqlData(items, description)

    # load session data from redis
    with (yield from redis_pool) as redis:
        redis_user_data = yield from redis.get("{}_{}".format(AIOHTTP_SESSION, session.identity))
        redis_admin_data = yield from redis.get("{}_{}".format(AIOHTTP_SESSION, session_key_admin))

    redis_user_data_dict = {}
    redis_admin_data_dict = {}
    #redis_user_data={'created': 1453960118, 'session': {'is_admin': False, 'last_visit': 1458546120.7152512, 'host': '127.0.0.1', 'nickname': 'Ivan'}}
    redis_user_data_dict[session.identity] = json.loads(redis_user_data.decode('ascii'))
    redis_admin_data_dict[session_key_admin] = json.loads(redis_admin_data.decode('ascii'))

    logger.debug("redis_user_data_dict={}".format(redis_user_data_dict))
    logger.debug("redis_admin_data_dict={}".format(redis_admin_data_dict))

    #for i in items:
    #    logger.debug("ID={}".format(handle_data.get("id", i)))

    #item = await cur.fetchone()
    #for i in item:
    #    logger.info("cur.fetchone = {}".format(i))

    return aiohttp_jinja2.render_template('chat.html', request,
                                          {"test": "test",
                                           "sql_data": sql_data,
                                           "redis_user_data_dict": redis_user_data_dict,
                                           "redis_admin_data_dict": redis_admin_data_dict})


async def new_msg(request):
    """
    The function is executed every time when message is sended throught post request
    """
    global admins, queues_admin, queues
    message = ""
    logger.debug("admins = {}".format(str(admins)))
    logger.debug("queues = {}".format(str(queues)))
    logger.debug("queues_admin = {}".format(str(queues_admin)))

    global loop
    session = await get_session(request)
    nickname = session['nickname']
    form_data = await request.post()
    host = request.host[:request.host.find(':')] # host
    read_task = loop.create_task(request.content.read())

    message_json = (await read_task).decode('utf-8')
    logger.debug("message_json={}".format(message_json))
    if message_json:
        message = json.loads(message_json)['message']
        logger.debug("message={}".format(message))
    else:
        logger.debug(form_data)
    dt = datetime.utcnow()
    sql = """insert into chat_message(message, session_key, dt, other_session_key)
             values (%s, %s, %s, %s)"""

    if session['is_admin'] == True:
        await sql_execute(sql, False, (message, session.identity, dt, form_data['to']))
    else:
        to = queues[session.identity]['to'] # get "to" from queues dict
        await sql_execute(sql, False, (message, session.identity, dt, to))

    await send_message(host, session, message, nickname, form_data=form_data)

    return web.Response(body=b'OK')

def myfilter(value):
    return value.upper()

def get(item_data, item_name):
    return item_data.get(item_name)

async def init(loop):
    global app, dbpool, srv, redis_pool
    redis_pool = await aioredis.create_pool(('localhost', 6379))
    storage = redis_storage.RedisStorage(redis_pool)
    session_middleware1 = session_middleware(storage)

    db_settings['dbpool'] = await aiopg.create_pool(dsn)

    app = web.Application(middlewares=[session_middleware1])
    #app = web.Application(middlewares=[session_middleware(
    #    EncryptedCookieStorage(b'Thirty  two  length  bytes  key.'))])
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader(path('apps/ws_chat/templates')))
    app['aiohttp_jinja2_environment'].filters['myfilter'] = myfilter
    app['aiohttp_jinja2_environment'].filters['get'] = get
    # app.router.add_route('GET', '/test/ws/', ws_test)
    app.router.add_static('/media/', path('media/'), name='media')
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
    global srv, redis
    #await handler.finish_connections(1.0)
    srv.close()
    await srv.wait_closed()
    await app.finish()
    await redis.clear()

#print('serving on', srv.sockets[0].getsockname())

if __name__ == "__main__":
    loop.run_until_complete(init(loop))
    logger.info("Server start")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(end())
    loop.close()
