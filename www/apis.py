# -*- coding: utf-8 -*-
import re
import json
import hashlib
from aiohttp import web
from config import configs
from route import post
from models import User, next_id
from controller import generate_cookie
from api_errors import APIError, APIValueError
from controller import generate_cookie
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')
_COOKIE_KEY = configs['session']['secret']
COOKIE_NAME = configs['cookie_name']


@post('/api/login')
def login(*, name, password):
    print(name, password)
    if not name:
        raise APIValueError('name', 'Invalid name.')
    if not password:
        raise APIValueError('password', 'Invalid password.')
    users = yield from User.find_all('name=?', (name,))
    if len(users) == 0:
        raise APIValueError('name', 'user name not exist.')
    user = users[0]
    sha1_password = '%s:%s' % (user.id, password)
    password = hashlib.sha1(sha1_password.encode('utf-8')).hexdigest()

    if user.password != password:
        raise APIValueError('password', 'Invalid password.')
    r = web.Response()
    r.set_cookie(
        COOKIE_NAME,
        generate_cookie(user, 86400),
        max_age=86400,
        httponly=True
    )
    user.password = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@post('/api/sign_up')
def api_user_sign_up(*, name, password):
    """
    password = sha1((uid + ':' + password).encode(utf-8))
    """
    if not name or not name.strip():
        raise APIValueError('name')
    if not password or not _RE_SHA1.match(password):
        raise APIValueError('password')

    all_users = yield from User.find_all('name=?', [name])

    if len(all_users):
        raise APIError('sign up failed', 'name', 'User name already exist')
    uid = next_id()
    sha1_password = '%s:%s' % (uid, password)
    password = hashlib.sha1(sha1_password.encode('utf-8')).hexdigest()
    user = User(id=uid, name=name.strip(), password=password, is_admin=True)
    yield from user.save()
    r = web.Response()
    cookie_name = configs['cookie_name']
    r.set_cookie(
        cookie_name, generate_cookie(user, 86400), max_age=86400, httponly=True
    )
    user.password = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r
