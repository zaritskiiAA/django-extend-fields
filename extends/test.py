import inspect
from inspect import FrameInfo
from contextlib import ContextDecorator
#from django.utils.translation import override


class Question:

    def __init__(self, param=10):
        self.question = 'question'

    def __setattr__(self, name: str, value) -> None:
        super().__setattr__(name, value)


class _Inspector:

    def __init__(self, frame):
        self.frame = frame
        self.begin = frame.f_lineno
        self.end = None
        print(inspect.getsourcelines(self.frame)[0][self.begin-1:])
        print(self.begin)


class _StageSwitcher:

    def __set_name__(self, cls, attr):
        self._attr = attr

    def __get__(self, obj, objtype=None):
        
        if obj is None:
            return self
        
        getattr(self, self._attr.lower())(obj)

    def begin(self, obj):
        obj._inspector = _Inspector(inspect.currentframe().f_back.f_back)

    def end(self, obj):
        obj._inspector.end = obj._inspector.frame.f_lineno


class ExposeAttrs:

    BEGIN = _StageSwitcher()
    END = _StageSwitcher()

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    

q = Question()

with ExposeAttrs() as expose:
    expose.BEGIN
    q.question = 10
    q.question = 11
    # frame = expose.inspector.frame
    # lineno = expose.inspector.start_lineno
    # print(lineno)
    # print(inspect.getsourcelines(frame)[0][lineno-1:])
    # for i in range(10):
    #     pass
    expose.END
   

a = 10


import asyncio
import random

users = ['user1', 'user2', 'user3']
products = ['iPhone 14', 'Samsung Galaxy S23', 'MacBook Pro', 'Dell XPS 13', 'Sony WH-1000XM5', 'Apple Watch Series 8', 'Kindle Paperwhite', 'GoPro Hero 11', 'Nintendo Switch', 'Oculus Quest 2']
actions = ['просмотр', 'покупка', 'добавление в избранное']

class AsyncIterator:
    
    async def __aiter__(self):
        return self
    
    async def __anext__(self):
        user, action, product = random.choice(users), random.choice(products), random.choice(actions)
        await asyncio.sleep(0)
        return {'user_id': user, 'action': action, 'product_id': product}

async def user_action_generator():
    
    while True:
        yield {
            'user_id': random.choice(users), 
            'action': random.choice(products), 
            'product_id': random.choice(actions),
        }


async def main():

    stop = 0
    async for data in user_action_generator():
        print(data)
        # stop += 1
        # if stop == 1000:
        #     print(stop)
        #     break

asyncio.run(main())