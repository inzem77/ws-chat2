import asyncio
import aiohttp

await def fetch_page(client, url):
    async with client.get(url) as response:
        assert response.status == 200
        return await response.read()

loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)
content = loop.run_until_complete(
    fetch_page(client, 'http://python.org'))
print(content)
client.close()
