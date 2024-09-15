from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
from django.http import HttpResponse
from .models import Post, Comment
from .forms import PostForm, CommentForm

from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

def index(request):
    return HttpResponse('Hello, Blog!')

def get_post_list(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    # return render(request, "posts_list.html", {'posts': posts})
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts_list.html', {'page_obj': page_obj})

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    return render(request, "post_detail.html", {'post': post, 'comments': comments})

@login_required(login_url="/blog/login/")
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            return redirect('blog:post_list')
    else:
        form = PostForm()
    
    return render(request, 'create_post.html', {'form': form})

@login_required(login_url="/blog/login/")
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            url = reverse('blog:post_detail', args=[post_id])
            return redirect(url)
    else:
        form = PostForm(instance=post)
    return render(request, 'edit_post.html', {'form': form})

@login_required(login_url="/blog/login/")
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # Ensure that only the author can delete the post
    if post.author != request.user:
        return redirect('blog:post_list')

    if request.method == 'POST':
        post.delete()
        return redirect('blog:post_list')

    return render(request, 'delete_post.html', {'post': post})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after registration
            return redirect('blog:post_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # log in the user
            user = form.get_user()
            # print('here is user:', type(user), user)
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('blog:post_list')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('blog:post_list')

@login_required
def create_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        comment = CommentForm(request.POST)
        if comment.is_valid():
            instance = comment.save(commit=False)
            instance.author = request.user
            instance.post = post
            instance.save()
            url = reverse('blog:post_detail', args=[post_id])
            return redirect(url)
    else:
        comment = CommentForm()
    comments = post.comments.all()
    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,  # Display all comments
        'comment_form': comment,  # Include the form in the context
    })