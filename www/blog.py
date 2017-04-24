# -*- coding: utf-8 -*-
import markdown2
from route import get
from models import User, Blog, Categery
from controller import get_page_index, check_admin, login


@get('/blogs')
def index(request):
    users = yield from User.find_all('is_admin=?', True)
    blogs = yield from Blog.find_all()
    return dict(__template__='blogs.html', users=users, blogs=blogs)


@get('/blog/{blog_id}')
def get_blog(blog_id):
    blog = yield from Blog.find(id)
    blog.marked_content = markdown2.markdown(blog.content)
    return dict(__template__=blog.html, blog=blog)


@get('/x/admin/blogs/add_blog')
def add_blog():
    all_categeries = yield from Categery.find_all()
    return dict(
        __template__='edit_blog.html',
        id='',
        all_categeries=all_categeries,
        action='/api/add_blog'
    )


@get('/x/admin/blogs/edit_categery/{categery_id}')
def edit_categery(request, *, categery_id):
    categery = None
    if categery_id:
        categery = yield from Categery.find(categery_id)
    return dict(
        __template__='edit_categery.html',
        id=categery_id,
        categery=categery,
        action='/api/edit_categery'
    )


@get('/x/admin/blogs/add_categery')
def add_categery():
    return dict(
        __template__='edit_categery.html',
        action='/api/add_categery'
    )


@get('/x/admin/blogs/edit_blog/{blog_id}')
def edit_blog(request, *, blog_id):
    return dict(
        __template__='edit_blog.html',
        id=blog_id,
        action='/api/add_blog'
    )


@get('/blog/{title_en}')
def get_blog_by_title_en(request, *, title_en):
    blog = Blog.find_all("title_en=?", (title_en,))
    blog.marked_content = markdown2.markdown(blog.content)
    return dict(
        __template__='blog_show.html',
        id=blog.id,
        blog=blog
    )


@get('/x/admin/manage_blogs')
def manage_blogs(*, page='1'):
    return dict(
        __template__='manage_blogs.html',
        page_index=get_page_index(page)
    )


@get('/x/admin/manage_categeries')
def manage_categeries(request):
    return dict(
        __template__='manage_categeries.html',
    )
