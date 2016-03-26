Asyncio websocket chat apps.
The main technologies: Python 3.5, Asyncio, Django, pyQt5
Admin client wrote with Qt5 library. Every message from web user comes to admin user. The history of messages loads from Postgres DB. Admins of chat authenticate throught django admin users. 
Order of launch apps: django app, admin app, client app.
Client app - ws_chat/apps/ws_chat/chat.py
Admin app - ws_chat/apps/admin_client/main.py

