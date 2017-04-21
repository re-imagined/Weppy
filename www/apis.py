# -*- coding: utf-8 -*-
import re
import json
import hashlib
from aiohttp import web
from config import configs
from route import post, get
from models import User, Blog, Categery, next_id
from api_errors import APIError, APIValueError
from controller import generate_cookie, COOKIE_NAME

_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@post('/api/login')
def login(*, name, password):
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

    all_users = yield from User.find_all('name=?', (name,))

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


@post('/api/add_blog')
def api_add_blog(
        request, *, title, title_en, summary, content, created_at, categery_id
):
    # check_admin(request)
    if not title or not title.strip():
        raise APIValueError('title', 'title cannot be empty.')
    if not title_en or not title_en.strip():
        raise APIValueError('title_en', 'title_en cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    if not created_at or not created_at.strip():
        raise APIValueError('created_at', 'content cannot be empty.')
    if not categery_id or not categery_id.strip():
        raise APIValueError('created_at', 'content cannot be empty.')
    blog = Blog(
        title=title.strip(),
        title_en=title_en.strip(),
        content=content.strip(),
        summary=summary.strip(),
        created_at=created_at.strip(),
        categery_id=int(categery_id.strip())
    )

    yield from blog.save()

    return blog


@post('/api/edit_blog')
def api_edit_blog(
        request, *, blog_id, title, title_en,
        summary, content, created_at, categery_id
):
    # check_admin(request)
    if not title or not title.strip():
        raise APIValueError('title', 'title cannot be empty.')
    if not title_en or not title_en.strip():
        raise APIValueError('title_en', 'title_en cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    if not created_at or not created_at.strip():
        raise APIValueError('created_at', 'content cannot be empty.')

    blog = yield from Blog.find(blog_id.strip())
    blog.title = title.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    blog.created_at = created_at.strip(),
    blog.categery_id = categery_id.strip()
    blog.title_en = title_en.strip()

    yield from blog.update()

    return blog


@post('/api/add_categery')
def api_add_categery(request, *, name):
    # check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    categery = Categery(name=name.strip())
    yield from categery.save()
    return categery


@get('/api/get_blog/{blog_id}')
def api_get_blog(request, *, blog_id):
    blog = yield from Blog.find(blog_id.strip())
    return blog
