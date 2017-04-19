# -*- coding: utf-8 -*-
from route import get
from models import User
import asyncio


@get('/')
@asyncio.coroutine
def index(request):
    users = yield from User.find_all('is_admin=?', True)
    return {
        '__template__': 'test.html',
        'users': users
    }
