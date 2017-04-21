# -*- coding: utf-8 -*-
import markdown2
from route import get
from models import User, Blog, Categery


@get('/blogs')
def index(request):
    users = yield from User.find_all('is_admin=?', True)
    blogs = yield from Blog.find_all()
    return {
        '__template__': 'blogs.html',
        'users': users,
        'blogs': blogs
    }


@get('/blog/{blog_id}')
def get_blog(blog_id):
    blog = yield from Blog.find(id)
    # blog.html_content = markdown2.markdown(blog.content)
    return{
        '__template__': 'blog.html',
        'blog': blog
    }


@get('/x/admin/blogs/add_blog')
def add_blog():
    all_categeries = yield from Categery.find_all()
    return {
        '__template__': 'edit_blog.html',
        'id': '',
        'all_categeries': all_categeries,
        'action': '/api/add_blog'
    }


@get('/x/admin/blogs/add_categery')
def add_categery():
    return {
        '__template__': 'edit_categery.html',
        'id': '',
        'action': '/api/add_categery'
    }


@get('/x/admin/blogs/edit_blog/{blog_id}')
def edit_blog(request, *, blog_id):
    return {
        '__template__': 'edit_blog.html',
        'id': blog_id,
        'action': '/api/add_blog'
    }


@get('/blog/{title_en}')
def get_blog_by_title_en(request, *, title_en):
    blog = Blog.find_all("title_en=?", (title_en,))
    blog.marked_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog_show.html',
        'id': blog.id,
        'blog': blog
    }
