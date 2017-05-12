# -*- coding: utf-8 -*-
import re
import json
import hashlib
import logging
from aiohttp import web
from config import configs
from route import post, get
from models import User, Blog, Categery, next_id
from api_errors import APIError, APIValueError
from controller import (
    generate_cookie, COOKIE_NAME, Page, get_page_index, check_admin
)

logging.basicConfig(level=logging.INFO)

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
    if not check_admin(request):
        return dict(message='no permition')
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
        request, *, id, title, title_en,
        summary, content, created_at, categery_id
):
    if not check_admin(request):
        return dict(message='no permition')
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

    blog = yield from Blog.find(id.strip())
    blog.title = title.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    blog.created_at = created_at.strip(),
    blog.categery_id = categery_id.strip()
    blog.title_en = title_en.strip()

    yield from blog.update()

    return blog


@post('/api/delete_blog')
def api_delete_blog(request, *, id):
    if not check_admin(request):
        return dict(message='no permition')
    if not id:
        raise APIValueError('ID', 'ID is Invalid')
    print(id)
    blog = yield from Blog.find(id)
    yield from blog.remove()
    return dict(id=id)


@post('/api/add_categery')
def api_add_categery(request, *, name):
    if not check_admin(request):
        return dict(message='no permition')
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    categery = Categery(name=name.strip())
    yield from categery.save()
    return categery


@post('/api/edit_categery')
def api_edit_categery(request, *, id, name):
    if not check_admin(request):
        return dict(message='no permition')
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not id or not id.strip():
        raise APIValueError('categery_id', 'categery_id cannot be empty.')
    categery = yield from Categery.find(int(id.strip()))
    categery.name = name
    yield from categery.update()
    return categery


@get('/api/get_categery/{categery_id}')
def api_get_categery(request, *, categery_id):
    categery = yield from Categery.find(categery_id)
    return dict(categery=categery)


@get('/api/get_all_categeries')
def api_get_all_categeries(request):
    categeries = yield from Categery.find_all()
    return dict(categeries=categeries)


@get('/api/get_blog/{blog_id}')
def api_get_blog(request, *, blog_id):
    if not blog_id or not blog_id.strip():
        raise APIValueError('blog_id', 'blog_id cannot be empty.')
    blog = yield from Blog.find(blog_id.strip())
    categery = yield from Categery.find(blog.categery_id)
    blog.categery_name = categery.name
    time = str(blog.created_at).split()
    blog.created_at = time[0]
    return dict(blog=blog)


@get('/api/get_blogs')
def api_get_blogs(request, *, page='1'):
    """
    get blogs by the given page information
    """
    page_index = get_page_index(page)
    num = yield from Blog.get_count('id')
    page = Page(num, page_index)
    if num == 0:
        return dict(page=page, blogs=())
    blogs = yield from Blog.find_all(
        orderBy='id desc', limit=(page.offset, page.limit)
    )
    for blog in blogs:
        time = str(blog.created_at).split()
        blog.created_at = time[0]
        categery = yield from Categery.find(blog.categery_id)
        blog.categery_name = categery.name
    return dict(
        page=page,
        blogs=blogs
    )


@get('/api/get_blog_by_categery_id/{categery_id}')
def api_get_blog_by_categery_id(request, *, categery_id, page='1'):
    if not categery_id or not categery_id.strip():
        raise APIValueError('categery_id', 'categery_id cannot be empty.')
    num = yield from Blog.get_count(
        'id', 'categery_id=?',
        (categery_id.strip(),)
    )
    page_index = get_page_index(page)
    page = Page(num, page_index)
    blogs = yield from Blog.find_all(
        'categery_id=?',
        (categery_id.strip(),),
        orderBy='id desc',
        limit=(page.offset, page.limit)
    )
    for blog in blogs:
        time = str(blog.created_at).split()
        blog.created_at = time[0]
        categery = yield from Categery.find(blog.categery_id)
        blog.categery_name = categery.name
    return dict(
        page=page,
        blogs=blogs
    )
