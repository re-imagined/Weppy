# -*- coding: utf-8 -*-

from route import get
from models import User, Blog, Categery
from controller import get_page_index, check_admin, Page, mark


@get('/blogs')
def index(request):
    users = yield from User.find_all('is_admin=?', True)
    blogs = yield from Blog.find_all()
    return dict(__template__='blogs.html', users=users, blogs=blogs)


@get('/x/admin/blogs/add_blog')
def add_blog(request):
    if not check_admin(request):
        return 'redirect:/login'
    else:
        all_categeries = yield from Categery.find_all()
        return dict(
            __template__='edit_blog.html',
            id='',
            all_categeries=all_categeries,
            action='/api/add_blog'
        )


@get('/x/admin/blogs/edit_categery/{categery_id}')
def edit_categery(request, *, categery_id):
    if not check_admin(request):
        return 'redirect:/login'
    else:
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
def add_categery(request):
    if not check_admin(request):
        return 'redirect:/login'
    else:
        return dict(
            __template__='edit_categery.html',
            action='/api/add_categery'
        )


@get('/x/admin/blogs/edit_blog/{blog_id}')
def edit_blog(request, *, blog_id):
    if not check_admin(request):
        return 'redirect:/login'
    else:
        return dict(
            __template__='edit_blog.html',
            id=blog_id,
            action='/api/edit_blog'
        )


@get('/blog/{title_en}')
def get_blog_by_title_en(request, *, title_en):
    blog = yield from Blog.find_all("title_en=?", (title_en,))
    blog = blog[0]
    # blog.marked_content = markdown(blog.content)
    blog.marked_content = mark(
        blog.content,
    )
    del blog['content']
    return dict(
        __template__='blog_show.html',
        id=blog.id,
        blog=blog
    )


@get('/x/admin/manage_blogs')
def manage_blogs(request, *, page='1'):
    if not check_admin(request):
        return 'redirect:/login'
    else:
        page_index = get_page_index(page)
        num = yield from Blog.get_count('id')
        page = Page(num, page_index)
        if num == 0:
            return dict(page=page, blogs=())
        print(page)
        return dict(
            __template__='manage_blogs.html',
            page=page
        )


@get('/x/admin/manage_categeries')
def manage_categeries(request):
    if not check_admin(request):
        return 'redirect:/login'
    else:
        return dict(
            __template__='manage_categeries.html',
        )
