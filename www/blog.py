# -*- coding: utf-8 -*-
from route import get
from models import User
import asyncio


@get('/')
@asyncio.coroutine
def index(request):
    users = yield from User.find_all()
    return {
        '__template__': 'test.html',
        'users': users
    }
