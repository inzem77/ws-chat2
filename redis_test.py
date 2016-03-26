import asyncio
import asyncio_redis

@asyncio.coroutine
def example():
    # Create Redis connection
    connection = yield from asyncio_redis.Connection.create(host='127.0.0.1', port=6379)

    # Set a key
    yield from connection.set('my_key', 'my_value')

    # When finished, close the connection.
    connection.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(example())
