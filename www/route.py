# -*- coding: utf-8 -*-
# router of the framework
from functools import wraps, partial


"""
wraps is used to fetch the parameters from calling,
but those parameters are not necessarily all the parameters we need
"""


def router(path, *, method):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args)
        wrapper.__method__ = "GET"
        wrapper.__route__ = path
        return wrapper
    return decorator

get = partial(router, method='GET')
post = partial(router, method='POST')
