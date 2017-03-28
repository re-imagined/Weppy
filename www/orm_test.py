import orm
from models import User
import asyncio


@asyncio.coroutine
def test():
    yield from orm.create_pool(loop, user='root', password='czh', db='weppy')
    user = User(name="admin", password='123', is_admin=True)
    yield from user.save()
    yield from orm.destory_pool()


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()
