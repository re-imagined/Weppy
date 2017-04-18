# -*- coding: utf-8 -*-
from models import User
from aiohttp import web
from route import get, post
import re, time, json, logging, hashlib, base64, asyncio
from api_errors import APIValueError, APIResourceNotFoundError
from config import configs
_COOKIE_KEY = configs['session']['secret']
COOKIE_NAME = configs['cookie_name']


def generate_cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    cookie_str = '%s-%s-%s-%s' % (user.id, user.password, expires, _COOKIE_KEY)
    cookie_lst = [
        user.id,
        expires,
        hashlib.sha1(cookie_str.encode('utf-8')).hexdigest()
    ]
    return '-'.join(cookie_lst)


@asyncio.coroutine
def get_user_by_cookie(cookie):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie:
        return None
    try:
        lst = cookie.split('-')
        if len(lst) != 3:
            return None
        uid, expires, sha1 = lst
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.password, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.password = '******'
        return user
    except Exception as e:
        logging.exception(e)


@get('/sign_up')
def sign_up():
    return {
        '__template__': 'sign_up.html'
    }


@get('/login')
def login():
    return {
        '__template__': 'login.html'
    }
