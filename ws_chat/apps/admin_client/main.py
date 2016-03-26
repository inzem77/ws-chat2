"""
# coding: utf8
import sys
import random
import asyncio
import time

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication, QProgressBar
from quamash import QEventLoop, QThreadExecutor

app = QApplication(sys.argv)
app.setApplicationName('ws_chat')
form_class, base_class = loadUiType('window.ui')

class MainWindow(QDialog, form_class):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        self.i = 0
        self.setupUi(self)

    def buttonClick(self):
        self.lineEdit.setText("Hello!")
        self.textEdit.append("Hello!")
        self.textEdit.copy()
        #if self.i>10:
        #self.textEdit.select(0, random.randint(0, self.i-5))
        #self.textEdit.selectAll()
        #self.textEdit.undo()
        #self.textEdit.selectWord()
        self.i += 1

    def otherButtonClick(self):
        self.textEdit.insertHtml("<br>Insert!")
        #self.textEdit.append(self.textEdit.length)


#-----------------------------------------------------#
form = MainWindow()
form.setWindowTitle('ws_chat')
form.show()
#sys.exit(app.exec_())

loop = QEventLoop(app)
asyncio.set_event_loop(loop)  # NEW must set the event loop

#progress = QProgressBar()
#progress.setRange(0, 99)
#progress.show()

# we can create next functional
# coonect to web socket server with send nickname by post request
# it must be created websocket connection

@asyncio.coroutine
def master():
    #yield from first_50()
    #with QThreadExecutor(1) as exec:
    #    yield from loop.run_in_executor(exec, last_50)
    ## TODO announce completion?


@asyncio.coroutine
def first_50():
    for i in range(50):
        progress.setValue(i)
        yield from asyncio.sleep(.5)

def last_50():
    for i in range(50,100):
        loop.call_soon_threadsafe(progress.setValue, i)
        time.sleep(.1)

with loop: ## context manager calls .close() when loop completes, and releases all resources
    loop.run_until_complete(master())

"""
import sys, os
import base64, binascii, pickle, json, hashlib
import asyncio
import requests
from datetime import datetime

import quamash
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QTextEdit, QMainWindow
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication, QProgressBar, QVBoxLayout
from PyQt5.QtCore import Qt

from quamash import QEventLoop, QThreadExecutor
import aiohttp

form_class, base_class = loadUiType('window.ui')

import logging
import json

FORMAT = '%(asctime)-15s %(funcName)s:%(lineno)d %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger(__file__)
FORMAT = 'mylog: %(asctime)-15s %(funcName)s:%(lineno)d %(message)s'
logger.setLevel(logging.DEBUG)

login_message_dict = {} # {session_key:{'nickname':'Ivan', 'messages':{'message':'Hello', 'datetime': 'datetime obj'}}}
item_id_session_key = {} # {list_item_id:'session_key_12312412'
session = None
nickname = ""
runflag = False
login = ""
password = ""
admin_session_key = ""

def save_login_password(login, password, admin_session_key=""):
    # Save login password in file
    pf = os.path.join(os.path.dirname(__file__), "psw")
    with open(pf, 'wb') as f:
        login_password = {"login": login, "password": password, "admin_session_key": admin_session_key}
        login_password = json.dumps(login_password)
        login_password = base64.b64encode(bytes(login_password, "utf-8"))
        f.write(login_password)


async def _sendMessage(message, to):
    global session
    async with session.post('http://127.0.0.1:8080/{}/'.format(session.host), data={
        'message': message,
        'to': to,
        }) as response:
        logger.debug(await response.text())


class MainWindow(QMainWindow, form_class):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        self.i = 0
        self.setupUi(self)


    def buttonClick(self):
        self.lineEdit.setText("Hello!")
        self.textEdit.append("Hello!")
        self.textEdit.copy()

        self.i += 1
        self.textEdit1 = QTextEdit(self)
        self.textEdit1.setFocus()
        self.textEdit1.setReadOnly(True)

    def addTab(self):
        tab = QWidget()
        self.textEdit.insertHtml("<br>Add tab!")
        self.tabWidget.addTab(tab, "new tab")
        #self.textEdit.append(self.textEdit.length)

    def tabClosed(self, index):
        self.textEdit.insertHtml("<br>Close tab")
        self.tabWidget.removeTab(index)

    def listItemClick(self):
        global login_message_dict, item_id_session_key
        logger.debug("click")
        listitem_id = self.listClients.currentRow()
        self.textEdit.setText("")
        for i in login_message_dict[item_id_session_key[listitem_id]]['messages']:
            self.textEdit.append("[{}:{}] {}: {}".format(
                i['datetime'].hour,
                i['datetime'].minute,
                login_message_dict[item_id_session_key[listitem_id]]['nickname'],
                i['message'],
            ))

    def buttonClickSendMessage(self):
        """
            take message from textMessage
            clean textMessage
            text from textMessage is sended to client through Web Socket
        """
        listitem_id = self.listClients.currentRow() # get currnet row from list of clients
        global loop, session
        dt = datetime.now()
        message = self.textMessage.toPlainText() # get message from text Edit
        self.textMessage.setText("") # clear Text Edit
        # add text to chat Text Edit
        self.textEdit.append("[{}:{}] {}: {}".format(
                                dt.hour,
                                dt.minute,
                                session.nickname,
                                message)
                            )
        loop.create_task(_sendMessage(message=message, to=item_id_session_key[listitem_id])) # send message to reciever

@asyncio.coroutine
def f():
    global runflag
    while True:
        data = yield
        logger.info("running.....")
        yield from asyncio.sleep(1) # sleep on 1 second
        if runflag == True:
            return True

#-----------------------------------------------------#
async def wait_messages(form):
    logger.debug("login={login}".format(login=login))
    logger.debug("password={password}".format(password=password))
    global login_message_dict, item_id_session_key, session, login, password, admin_session_key
    session = aiohttp.ClientSession()

    nickname = 'admin'

    flag = False
    flag = await f()

    if flag == True:
        with aiohttp.ClientSession() as session:# make session
            async with session.get('http://127.0.0.1:8025/admin/') as response:
                logger.info("Response from django is arived with status {}".format(response.status))
                assert response.status == 200
                csrftoken = response.cookies['csrftoken']
                logger.debug("csrftoken=%s", csrftoken.value)
                async with session.post('http://127.0.0.1:8025/admin/login/?next=/admin/', data={
                    'username': login,
                    "password": password,
                    'csrfmiddlewaretoken': csrftoken.value,
                    'next': '/admin/?next=/admin/'}) as response:
                    #logger.debug(await response.text())

                    if response.status == 200: # Autorization has passed

                        async with session.get('http://127.0.0.1:8080', data={
                                'nickname': nickname,
                                'login': login,
                                'password': password}) as response:
                            logger.info("Response from server with GET request is {}".format(response.status))
                            assert response.status == 200
                            session.host = response.host
                            session.nickname = nickname
                            #set admin_session_key into session for restore session between request
                            if admin_session_key:
                                session.cookies['AIOHTTP_SESSION'] = admin_session_key
                            else:
                                admin_session_key = session.cookies['AIOHTTP_SESSION'].value
                                save_login_password(login, password, admin_session_key)
                            logger.debug("AIOHTTP_SESSION={}".format(admin_session_key))

                        async with session.post('http://127.0.0.1:8080', data={'nickname': 'admin', 'login': login, 'password': password}) as response:
                            logger.info("Response from server with POST request is {}".format(response.status))
                            assert response.status == 200
                            print(await response.text())

                        async with session.ws_connect('http://127.0.0.1:8080/127.0.0.1/ws/') as ws:
                            logger.info("Web socket connection to server")
                            async for msg in ws: # we can send client
                                if msg.tp == aiohttp.MsgType.text:
                                    data_recived = json.loads(msg.data)
                                    logger.info("WebSocket response  {}".format(data_recived))
                                    # TODO we have to save discussion and load discussion in form.textEdit by click row listClients
                                    dt = datetime.now()

                                    if data_recived['session_key'] in login_message_dict:
                                        login_message_dict[data_recived['session_key']]['messages'].append(
                                            {"message": data_recived['message'],
                                             "datetime": dt}
                                        )
                                        logger.debug("login_message_dict = {}".format(login_message_dict))
                                        if item_id_session_key[form.listClients.currentRow()] == data_recived['session_key']: # if we have focus to active client
                                            form.textEdit.append("[{}:{}] {}: {}".format(
                                                dt.hour,
                                                dt.minute,
                                                data_recived['nickname'],
                                                data_recived['message'])
                                            )
                                    else:
                                        form.listClients.addItem(data_recived['nickname'])
                                        listitem_id = form.listClients.count()-1
                                        item_id_session_key[listitem_id] = data_recived['session_key']
                                        logger.debug("item_id_session_key = {}".format(item_id_session_key))
                                        login_message_dict[data_recived['session_key']] = \
                                            {'nickname': data_recived['nickname'],
                                             "listitem_id": listitem_id,
                                             "messages": [{"message": data_recived['message'], "datetime": dt }]
                                            }
                                        if len(item_id_session_key) == 1:
                                            form.listClients.setCurrentRow(0)
                                            form.textEdit.append("[{}:{}] {}: {}".format(
                                                dt.hour,
                                                dt.minute,
                                                data_recived['nickname'],
                                                data_recived['message'])
                                            )
                                            #item = form.listClients.takeItem(0)
                                            #form.listClients.setCurrentItem(item)
                                    logger.debug("login_message_dict = {}".format(login_message_dict))



async def wait_clients(form):
        """
        Function is for manage clients
        """
        pass

async def _go(form):
    """
    def on_timeout():
        print('Timeout')
        fut.set_result(True)
    #fut = asyncio.Future()
    timer = QTimer()
    timer.setSingleShot(True)
    timer.setInterval(2000)
    timer.start()
    timer.timeout.connect(on_timeout)
    print('Yielding until signal...')
    #yield from fut
    """
    #global loop
    #loop.create_task(await wait_messages(form))
    await wait_messages(form)
    #print(msg.data)
    print('Continuing execution after yield from')


"""
def getPassword():
    text, ok = QInputDialog.getText(None, "Attention", "Password?",
                                    QLineEdit.Password)
    if ok and text:
        print("password=%s" % text)
"""
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication, QPushButton, QLineEdit

class Login(QWidget):
    """
    Login class. Login and password form.
    """

    def __init__(self, main_form, run):
        super().__init__()
        self.main_form = main_form
        self.initUI()
        self.run = run


    def initUI(self):
        global login, password, admin_session_key
        self.setGeometry(300, 300, 200, 150)
        self.setWindowTitle('Message box')
        self.btn = QPushButton('Login', self)
        self.btn.move(20, 80)
        #self.btn.clicked.connect(self.login)
        self.btn.clicked.connect(self.login_ajax)

        self.login_lineedit = QLineEdit(self)
        self.login_lineedit.move(20, 20)
        self.password_lineedit = QLineEdit(self)
        self.password_lineedit.setEchoMode(2)
        self.password_lineedit.move(20, 50)

        # read login and password from file
        pf = os.path.join(os.path.dirname(__file__), "psw")
        with open(pf, 'rb') as f:
            login_password = f.read()
            login_password = base64.b64decode(login_password)
            login_password = login_password.decode('utf-8')
            if login_password:
                login_password = json.loads(login_password)
                self.login_lineedit.setText(login_password["login"])
                login = login_password["login"]
                self.password_lineedit.setText(login_password["password"])
                password = login_password["password"]
                admin_session_key = login_password["admin_session_key"]

        self.show()

    def login_ajax(self):
        """
        Checking login and password
        """
        global runflag, login, password, admin_session_key
        login = self.login_lineedit.text()
        password = self.password_lineedit.text()

        save_login_password(login, password, admin_session_key)

        # check login and password from django admin as ajax query
        r = requests.get('http://127.0.0.1:8025/admin/')
        cookies = r.cookies
        if r.status_code == 200:
            r = requests.post('http://127.0.0.1:8025/ajax_auth/login/', data={
                    'username': login,
                    'password': password,
                    'csrfmiddlewaretoken': cookies['csrftoken']},
                    cookies=cookies

            )
            answer = json.loads(r.text)
            logger.debug(r.text)
            if answer['success'] == True:
                self.main_form.show()
                self.hide()
                runflag = True
                return True
            else:
                reply = QMessageBox.question(self, 'Warning',
                    "You do not right to input login and password.", QMessageBox.Yes, QMessageBox.Yes)
                return False
            #if r.status_code == 200 :



    def closeEvent(self, event):
        """
        Close dialog window
        """
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

app = QApplication(sys.argv)
#sys.exit(app.exec_())
#getPassword()


with quamash.QEventLoop(app) as loop:
    #w = QMainWindow()
    #w.show()
    app.setApplicationName('ws_chat')
    form = MainWindow()
    form.setWindowTitle('ws_chat')
    def runner():
        global runflag
        while True:
            data = yield
            if data == "RUN":
                runflag = True
    run = runner()
    run.send(None)
    ex = Login(form, run)

    try:
        #loop.run_until_complete(_go())
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_go(form))
    finally:
        loop.close()
print('Coroutine has ended')

"""
# This block is working
loop = asyncio.get_event_loop()
loop.run_until_complete(master())
loop.close()
"""