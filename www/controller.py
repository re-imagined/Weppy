# -*- coding: utf-8 -*-
# this file defined some functions for
# handling coookie and general page
import time
import logging
import hashlib
import asyncio
from models import User
from config import configs
from route import get
from api_errors import APIPermissionError

_COOKIE_KEY = configs['session']['secret']
COOKIE_NAME = configs['cookie_name']


@asyncio.coroutine
def check_admin(request):
    if request.__user__ is None or not request.__user__.is_admin:
        raise APIPermissionError('user is None or not an admin.')
    user = yield from User.find(request.__user__.id)
    if user.is_admin != 1:
        raise APIPermissionError('user is None or not an admin.')


def generate_cookie(user, max_age):
    '''
    Generate cookie str by user.
    the cookie string is:
        'user_id-expiration-sha1(user_id-expiration-_COOKIE_KEY)'
    '''

    expiration = str(int(time.time() + max_age))
    cookie_str = '%s-%s-%s-%s' % (
        user.id, user.password, expiration, _COOKIE_KEY
    )
    cookie_lst = [
        user.id,
        expiration,
        hashlib.sha1(cookie_str.encode('utf-8')).hexdigest()
    ]
    return '-'.join(cookie_lst)


@asyncio.coroutine
def get_user_by_cookie(cookie):
    '''
    Parse cookie and load user if cookie is valid.
    split the cookie and get the encrypted part to validate
    '''
    if not cookie:
        return None
    try:
        lst = cookie.split('-')
        if len(lst) != 3:
            return None
        uid, expiration, sha1 = lst
        if int(expiration) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        valid = '%s-%s-%s-%s' % (uid, user.password, expiration, _COOKIE_KEY)
        if sha1 != hashlib.sha1(valid.encode('utf-8')).hexdigest():
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
