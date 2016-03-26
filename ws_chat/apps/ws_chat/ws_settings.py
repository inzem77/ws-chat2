import os
import logging
import asyncio
import aiopg


dsn = 'dbname=ws_chat user=ws_chat password=ws_chat host=localhost port=5432'
db_name = "ws_chat"
db_user = "ws_chat"
db_password = "ws_chat"
db_host = "localhost"
db_port = 5432
dsn = 'dbname={} user={} password={} host={} port={}'.format(db_name, db_user, db_password, db_host, db_port)
db_settings = dict()

admins = {} # admins['127.0.0.1']=[session_key_admin1, session_key_admin2]
queues = {} # queues[session_key]={'to':session_key_admin, 'queue':['message1', 'message2']}
queues_admin = {} # queues_admin[session_key_user]['queue']=["message1", "message2", "message3"]
#history = {} # we will show history from database
channels = []
app = None

FORMAT = '%(asctime)-15s %(funcName)s:%(lineno)d %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger(__file__)
FORMAT = 'mylog: %(asctime)-15s %(funcName)s:%(lineno)d %(message)s'
logger.setLevel(logging.DEBUG)

loop = asyncio.get_event_loop()
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '../'))
path = lambda *args: os.path.join(ROOT, *args)

AIOHTTP_SESSION = "AIOHTTP_SESSION"