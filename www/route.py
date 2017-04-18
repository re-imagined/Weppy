# -*- coding: utf-8 -*-
import logging
import inspect
import asyncio
import os
from aiohttp import web
from urllib import parse
from api_errors import APIError
from functools import wraps, partial


def router(path, *, method):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__method__ = method
        wrapper.__route__ = path
        return wrapper
    return decorator

get = partial(router, method='GET')
post = partial(router, method='POST')
# put = partial(router, method='PUT')
# delete = partial(router, method=r'DELETE')


def get_kwargs(func):
    args = []
    params = inspect.signature(func).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def get_required_kwargs(func):
    # get all required parameters' name with no default values
    args = []
    params = inspect.signature(func).parameters
    for name, param in params.items():
        if (param.kind == inspect.Parameter.KEYWORD_ONLY and
                param.default == inspect.Parameter.empty):
            args.append(name)
    return tuple(args)


def get_named_kwargs(func):
    # get all keyword only parameters' names
    args = []
    params = inspect.signature(func).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def has_named_kwargs(func):
    params = inspect.signature(func).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True
    return False


def has_var_kwargs(func):
    params = inspect.signature(func).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True
    return False


def has_request_args(func):
    sig = inspect.signature(func)
    params = sig.parameters
    has_found = False
    for name, param in params.items():
        if name == 'request':
            has_found = True
            continue
        if (has_found and
                (
                    param.kind != inspect.Parameter.VAR_POSITIONAL and
                    param.kind != inspect.Parameter.KEYWORD_ONLY and
                    param.kind != inspect.Parameter.VAR_KEYWORD)):
            raise ValueError(
                'request parameter must be the last named parameter\
                 in function: %s%s' % (func.__name__, str(sig))
            )
    return has_found


class RequestHandler(object):
    def __init__(self, app, func):
        self._app = app
        self._func = func
        self._has_request_args = has_request_args(func)
        self._has_var_kwargs = has_var_kwargs(func)
        self._has_named_kwargs = has_named_kwargs(func)
        self._named_kwargs = get_named_kwargs(func)
        self._required_kwargs = get_required_kwargs(func)

    @asyncio.coroutine
    def __call__(self, request):
        kwargs = None
        if (self._has_var_kwargs or self._has_named_kwargs or
                self._required_kwargs):
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type')
                content_type = request.content_type.lower()
                if content_type == 'application/json':
                    parameters = yield from request.json
                    if not isinstance(parameters, dict):
                        return web.HTTPBadRequest("It's not JSON serializable")
                    kwargs = parameters
                elif (content_type in (
                        'application/x-www-form-urlencoded',
                        'multipart/form-data')):
                    parameters = yield from request.post()
                    kwargs = dict(**parameters)
                else:
                    return web.HTTPBadRequest(
                        'Unsupported Content-Type: %s' % request.content_type
                    )
            if request.method == 'GET':
                query_string = request.query_string
                if query_string:
                    kwargs = dict()
                    for key, value in parse.parse_query_string(
                            query_string, True).items():
                        kwargs[key] = value[0]
        if kwargs is None:
            kwargs = dict(**request.match_info)
        else:
            if not self._has_var_kwargs and self._named_kwargs:
                # remove all unamed kwargs:
                copy = dict()
                for name in self._named_kwargs:
                    if name in kwargs:
                        copy[name] = kwargs[name]
                kwargs = copy
            # check named arg:
            for key, value in request.match_info.items():
                if key in kwargs:
                    logging.warning(
                        'Duplicate arg name in named arg and kwargs: %s' % key
                    )
                kwargs[key] = value
        if self._has_request_args:
            kwargs['request'] = request
        if self._required_kwargs:
            for name in self._required_kwargs:
                if name not in kwargs:
                    return web.HTTPBadRequest('Missing argument: %s' % name)
        logging.info('call with args: %s' % str(kwargs))
        try:
            r = yield from self._func(**kwargs)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    print("static: "+path)
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))


def add_route(app, func):
    method = getattr(func, '__method__', None)
    path = getattr(func, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(func))
    if (not asyncio.iscoroutinefunction(func) and
            not inspect.isgeneratorfunction(func)):
        func = asyncio.coroutine(func)
    logging.info(
        'add route %s %s => %s(%s)' % (
            method, path, func.__name__,
            ', '.join(inspect.signature(func).parameters.keys())
        )
    )
    app.router.add_route(method, path, RequestHandler(app, func))


def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n+1:]
        mod = getattr(
            __import__(module_name[:n], globals(), locals(), [name]), name
        )
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        func = getattr(mod, attr)
        if callable(func):
            method = getattr(func, '__method__', None)
            path = getattr(func, '__route__', None)
            if method and path:
                add_route(app, func)
