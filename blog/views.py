from django.shortcuts import render
from .models import Post, Comment
from django.db.models import Prefetch

# Create your views here.
def get_posts(request):
    posts = Post.objects.prefetch_related('comments').all()
    return render(request, 'posts.html', {'posts': posts})