# -*- coding: UTF-8 -*-
"""
Encapsulate the SQL to protect the server from injection
"""
import asyncio
import logging
import aiomysql


def log(sql, args=()):
    logging.info('SQL: %s' % sql)


@asyncio.coroutine
def create_pool(loop, **kargs):
    logging.info('creating database connection pool...')
    global __pool
    __pool = yield from aiomysql.create_pool(
        host=kargs.get('host', 'localhost'),
        port=kargs.get('port', 8800),
        user=kargs['user'],
        password=kargs['password'],
        db=kargs['db'],
        charset=kargs.get('charset', 'utf8'),
        autocommit=kargs.get('autocommit', True),
        maxsize=kargs('maxsize', 10),
        minsize=kargs('minsize', 1),
        loop=loop
    )


@asyncio.coroutine
def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (yield from __pool) as connection:
        cursor = yield from connection.cursor(aiomysql.DictCursor)
        yield from cursor.execute(sql.replace('?', '%s'), args or ())

        # use size parameter implement limit of result size
        if size:
            result = yield from cursor.fetchmany(size)
        else:
            result = yield from cursor.fetchall()
        yield from cursor.close()
        logging.info('rows returned: %s' % len(result))
        return result


@asyncio.coroutine
def execute(sql, args):
    log(sql)
    with (yield from __pool) as connection:
        try:
            cursor = yield from connection.cursor()
            yield from cursor.execute(sql.replace('?', '%s'), args)
            affected = cursor.rowcount
            yield from cursor.close()
        except BaseException as e:
            log(e)
            raise
        return affected


def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)


class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__, self.column_type, self.name)

    def __repr__(self):
        return '%s: %s' % (self.name, self.default)


class StringField(Field):
    def __init__(
        self, name=None, primary_key=False, default=None, ddl='varchar(100)'
    ):
        super().__init__(name, ddl, primary_key, default)


class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super.__init__(name, 'boolean', False, default)

    def __str__(self):
        return '<%s, %s:%s>' % (
            self.__class__, self.column_type, self.name
            )

    def __repr__(self):
        return '%s: %s' % (self.name, self.default)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

    def __str__(self):
        return '<%s, %s:%s>' % (
            self.__class__, self.column_type, self.name
            )

    def __repr__(self):
        return '%s: %s' % (self.name, self.default)


class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)
