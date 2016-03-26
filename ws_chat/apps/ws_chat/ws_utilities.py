import asyncio
import json
from apps.ws_chat.ws_settings import *
from aiohttp import web
from aiohttp_session import get_session, session_middleware, SimpleCookieStorage, redis_storage, session_middleware


async def send_message(host, session, message, nickname, form_data):
    global admins, queues_admin, queues
    """
    print('{}: {}'.format(nickname, message).strip())
    if host not in history.keys():
        history[host]= {}
    if nickname not in history[host].keys():
        history[host][nickname] = []
    history[host][nickname].append('{}: {}'.format(nickname, message))
    if len(history[host][nickname]) > 20:
        del history[host][nickname][:-10]
    """
    #for queue in queues:
    #    await queue.put((host, nickname, message))
    # Data comes from WS or as Post request from admin client
    data_for_send = {
        'session': session,
        'message': message if message else form_data['message'],
        'nickname': nickname,

    }
    logger.debug("data_for_send: {}".format(data_for_send))
    if session['is_admin']:
        await queues[form_data['to']]['queue'].put(data_for_send)
    else:
        # put data in queues_admin's Queue
        to = queues[session.identity]['to'] # get "to" from queues dict
        await queues_admin[to]['queue'].put(data_for_send)


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
    logger.debug("start websocket_handler()")
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
    #await send_message(host, 'system', 'We are connected to {} host!'.format(host))

    """
    if host in history:
        if nickname in history[host]:
            for message in list(history[host][nickname]):
                ws.send_str(message)
    """

    logger.debug("Before create_task()")
    echo_task = loop.create_task(echo_loop(ws, session))
    logger.debug("After create_task()")
    async for msg in ws:
        if msg.tp == aiohttp.MsgType.close:
            logger.debug('websocket connection closed')
            break
        elif msg.tp == aiohttp.MsgType.error:
            logger.error('ws connection closed with exception %s' % ws.exception())
            break
        else:
            logger.warning('ws connection received unknown message type %s' % msg.tp)

    #await send_message(host, 'system', '{} left!'.format(nickname))

    echo_task.cancel()
    await echo_task
    logger.debug("End websocket_handler()")
    return ws


async def echo_loop(ws, session):
    global admins, queues_admin, queues
    queue = asyncio.Queue()
    if session['is_admin']:
        queues_admin[session.identity]['queue'] = queue #
        logger.debug("session admin = {}".format(session.identity))
    else:
        queues[session.identity]['queue'] = queue #
        logger.debug("session client = {}".format(session.identity))
    try:
        while True:
            #host, name, message = await queue.get()
            #ws.send_str('{}: {}: {}'.format(host, name, message))
            data = await queue.get()
            data_for_send = {"nickname": data['session']['nickname'],
                             "session_key": data['session'].identity,
                             "message": data['message']}
            logging.debug("data_for_send={}".format(data_for_send))
            ws.send_str(json.dumps(data_for_send))

    finally:
        if session['is_admin']:
            del queues_admin[session.identity]['queue']
            logger.debug("delete queues_admin[{}]['queue']".format(session.identity))
        else:
            del queues[session.identity]['queue']
            logger.debug("delete queues[{}]['queue']".format(session.identity))

@asyncio.coroutine
def sql_execute(sql, flag_return=False, *args, **kwargs):
    item = None
    description = []
    with (yield from db_settings['dbpool']) as conn:
        cur = yield from conn.cursor()
        #yield from cur.execute('SELECT * from auth_user')
        #item = yield from cur.fetchone()
        yield from cur.execute(sql, *args, **kwargs)
        if flag_return == True:
            for i in cur.description:
                description.append(i[0])
            item = yield from cur.fetchall()
        #return cur
        #cur.close()
        #yield from conn.close()
    return item, description

class ItemSqlData(object):
    def __init__(self, item, enum_description):
        self.item = item
        self.iter_item = iter(item)
        self.enum_description = enum_description
        self.i = None

    def __iter__(self):
        return self

    def __next__(self):
        self.i = next(self.iter_item)
        return self

    def get(self, item_name):
        index = self.enum_description[item_name]
        c = 0
        for i in self.item:
            if c == index:
                return i
            c+=1
            if c>100:
                return

class HandleSqlData(object):
    def __init__(self, items, description):
        self.enum_description = {}
        self.items = items
        self._iter_items = items.__iter__()
        self.description = description
        self.item_sql_data = None

        for i, item in enumerate(description):
            self.enum_description[item] = i

    def __iter__(self):
        return self

    def __next__(self):
        next_item = next(self._iter_items)
        self.item_sql_data = ItemSqlData(next_item, self.enum_description)
        return self.item_sql_data

class Yrange:
    def __init__(self, n):
        self.i = 0
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.i < self.n:
            i = self.i
            self.i += 1
            return i
        else:
            raise StopIteration()