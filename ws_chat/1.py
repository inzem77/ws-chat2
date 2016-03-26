import math

"""
def gen(n):
    x = list(range(n))
    for i in x:
        yield "i="+str(i)
    y = list(range(n))
    for j in y:
        yield "j="+str(j)

g=gen(3)
for i in g:
    print(i)
"""
def get_primes(number):
    while True:
        if is_prime(number):
            yield number
        number += 1

# not germane to the example, but here's a possible implementation of
# is_prime...

def is_prime(number):
    if number > 1:
        if number == 2:
            return True
        if number % 2 == 0:
            return False
        for current in range(3, int(math.sqrt(number) + 1), 2):
            if number % current == 0:
                return False
        return True
    return False


def solve_number_10():
    # She *is* working on Project Euler #10, I knew it!
    total = 2
    for next_prime in get_primes(3):
        if next_prime < 2000000:
            total += next_prime
        else:
            print(total)
            return

#solve_number_10()


import random

def get_data():
    """Return 3 random integers between 0 and 9"""
    return random.sample(range(10), 3)

def consume():
    """Displays a running average across lists of integers sent to it"""
    running_sum = 0
    data_items_seen = 0

    while True:
        data = yield
        data_items_seen += len(data)
        running_sum += sum(data)
        print('The running average is {}'.format(running_sum / float(data_items_seen)))

def produce(consumer):
    """Produces a set of values and forwards them to the pre-defined consumer
    function"""
    while True:
        data = get_data()
        print('Produced {}'.format(data))
        consumer.send(data)
        yield
"""
if __name__ == '__main__':
    consumer = consume()
    consumer.send(None)
    producer = produce(consumer)

    for _ in range(10):
        print('Producing...')
        next(producer)
"""

def foo1():
    """
    #Do something
    """
    while True:
        x = yield
        print("from foo1", x)

def foo():
    while True:
        x = yield
        print("x=", x)
        x1 = foo1()
        #x1.send(None)
        #x1.send("!@#!@#")
        yield x1
        #print("!!!")
        print(x1)
        y = yield
        print("y=", y)
    #x = yield
    #x = 12 + (yield 42)
    #x = 12 + (yield)
    #foo(yield 42)
    #foo(yield)

f = foo()
f.send(None) # you can write f.next()
f1 = f.send(11)
f1.send(None)
f1.send("!@#!@#")
f.send(None)
f.send(1)
f.close()

def coroutine(f):
    def wrpap(*args, **kwargs):
        gen = f(*args, **kwargs)
        gen.send(None)
        return gen
    return wrpap

@coroutine
def gen_plus():
    while True:
        x, y = (yield)
        print(x+y)

g = gen_plus()
g.send((1,22))
g.close()

def myfun1():
    for i in [1,2,3,4,5]:
        yield i

def myfun():
    while True:
        v1 = myfun1()
        print(v1.next())
        yield v1

#for i in myfun():
#    print(i)

import aiohttp, asyncio
async def main():
    """
    url = 'http://httpbin.org/cookies'
    async with aiohttp.ClientSession({'cookies_are': 'working'}) as session:
        async with session.get(url) as resp:
            assert await resp.json() == {"cookies":
                                             {"cookies_are": "working"}}
    """
    url = 'http://httpbin.org/cookies'
    cookies = dict(cookies_are='working')
    #session = aiohttp.ClientSession(cookies=cookies)
    async with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.get(url) as resp:
            text = await resp.json()
            print(text)
            assert text == {"cookies": {"cookies_are": "working"}}

        session.cookies['cookies_are'] = 'i have changed cookies'
        async with session.get(url) as resp:
            text = await resp.json()
            print(text)
            assert text == {"cookies": {"cookies_are": "i have changed cookies"}}

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

#asyncio.ensure_future(main())
#loop.run_forever()
#loop.close()



ll = [[1,2,3], [4,5,6], [7,8,9]]
ill = iter(ll)
