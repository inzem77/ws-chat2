import asyncio
import sys, os
import requests
import aiohttp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '../')))
from apps.ws_chat.chat import WebSocketResponse

"""
async def fetch(client):
    async with client.get('http://127.0.0.1:8080') as resp:
        assert resp.status == 200
        print(await resp.text())

with aiohttp.ClientSession() as client:
    asyncio.get_event_loop().run_until_complete(fetch(client))
"""
"""
We have to have list people who is connected to ws chat
When admin have connected to ws chat he recives list active clients and clients can send to him messages
We can create loop which will show list of links to active clients for which admin can go into chat room and begin discussion

"""

async def hello_world():
    # we do post request to server
    # we recive response and save data to session
    # In the cycle we send websocket data
    with aiohttp.ClientSession() as session:# make session
        async with session.post('http://127.0.0.1:8080', data={'nickname': 'Admin'}) as response:
            assert response.status == 200
            print(await response.text())

        async with session.ws_connect('http://127.0.0.1:8080/127.0.0.1/ws/') as ws:
            async for msg in ws:
                if msg.tp == aiohttp.MsgType.text:
                    print(msg.data)

        i=0
        while i<10:
            #127.0.0.1:8080/127.0.0.1/
            print("Hello World!")
            i+=1
            await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Blocking call which returns when the hello_world() coroutine is done

    loop.run_until_complete(hello_world())
    #loop.run_forever()
    loop.close()
