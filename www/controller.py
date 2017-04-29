# -*- coding: utf-8 -*-
# this file defined some functions for
# handling coookie and general page
import time
import logging
import hashlib
import asyncio
from route import get
from aiohttp import web
from models import User
from config import configs
from api_errors import APIPermissionError


logging.basicConfig(level=logging.INFO)

_COOKIE_KEY = configs['session']['secret']
COOKIE_NAME = configs['cookie_name']


@get('/base')
def base():
    return {
        '__template__': 'base.html'
    }


@get('/timepickertest')
def timepickertest():
    return {
        '__template__': 'timepickertest.html'
    }


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


@get('/logout')
def logout():
    r = web.Response()
    r.del_cookie(COOKIE_NAME)
    r.content_type = 'application/json'
    r.body = None
    return r


def check_admin(request):
    logging.info('Checking admin...')
    if request.__user__ is None or not request.__user__.is_admin:
        logging.warn('Not an admin')
        # raise APIPermissionError('Not an admin')
    else:
        logging.info('Admin confirmed')
        return True


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


class Page(object):
    def __init__(self, item_count, page_index=1, page_size=10):
        """
        item_count: number of total items you want to show in all page
        page_index: current page index
        page_size: number of items you want to show in each page
        """
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count // page_size + (
            1 if (item_count % page_size) > 0 else 0
            )
        if (int(page_size) == 0) or (int(page_index) > self.page_count):
            self.offset = 0
            self.limit = 0
            self.page_index = 1
        else:
            self.page_index = page_index
            self.offset = self.page_size * (page_index - 1)
            self.limit = self.page_size
        self.has_next = self.page_index < self.page_count
        self.has_previous = self.page_index > 1

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size: %s, \
            offset: %s, limit: %s, has_next: %s, has_previous: %s' % (
                self.item_count,
                self.page_count,
                self.page_index,
                self.page_size,
                self.offset,
                self.limit,
                self.has_next,
                self.has_previous
            )
    __repr__ = __str__


def get_page_index(page_str):
    page = 1
    try:
        page = int(page_str)
    except ValueError as e:
        pass
    if page < 1:
        page = 1
    return page
