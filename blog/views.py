from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import Post, Comment
from django.db.models import Prefetch

from django.views.decorators.cache import cache_page
from django.core.cache import cache

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from .forms import *


# Create your views here.

@cache_page(60)
def get_posts(request):
    posts = Post.objects.prefetch_related('comments').all()
    return render(request, 'posts.html', {'posts': posts})

def get_post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'post_detail.html', post_detail_info(post, post_id))

def post_detail_info(post, post_id):
    comments = post.comments.select_related('author')
    recent_comments = comments.order_by('-created_date')[:5]

    # check comments number in cache
    comment_num = cache.get(f'comment_num_{post_id}')
    if comment_num is None:
        comment_num = comments.count()
        cache.set(f'comment_num_{post_id}', comment_num, timeout=60)


    return {
        'post': post,
        'comment_num': comment_num,
        'comments': recent_comments,
        }

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        print('post request:', request.POST)
        form = CommentForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.post = post
            instance.save()

            cache.delete(f'recent_comments_{post_id}')
            cache.delete(f'comment_num_{post_id}')
            return redirect('blog:post_detail', post_id=post_id)

        else:
            form = CommentForm()

    post_detail_dict = post_detail_info(post, post_id)
    post_detail_dict['comment_form'] = form

    return render(request, 'post_detail.html', post_detail_dict)


from django.http import HttpResponse
def test_cache_view(request):
    cache.set('test_key', 'Hello, Redis!', timeout=60)  # Set a key
    return HttpResponse('Cached a value!')