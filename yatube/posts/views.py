from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import get_page_context


def index(request):
    post_list = Post.objects.all()
    template = 'posts/index.html'
    context = get_page_context(post_list, request)
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    post_list = Post.objects.filter(group=group)
    context = {
        'post_list': post_list,
        'group': group,
    }
    context.update(get_page_context(post_list, request))
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    template = 'posts/profile.html'
    post_count = post_list.count
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    context = {
        'author': author,
        'post_count': post_count,
        'following': following,
    }
    context.update(get_page_context(post_list, request))
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = post.author.posts.count()
    template = 'posts/post_detail.html'
    form = CommentForm(request.POST or None)
    comments = Comment.objects.all()
    context = {
        'post_count': post_count,
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    template = 'posts/create_post.html'
    if form.is_valid():
        create_posts = form.save(commit=False)
        create_posts.author = request.user
        create_posts.save()
        return redirect('posts:profile', create_posts.author)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, pk=post_id)
    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'comment': comment,
    }
    return render(request, 'posts:post_detail.html', context)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user
    )
    template = 'posts/follow.html'
    context = get_page_context(post_list, request)
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    user_dislake = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username,
    )
    user_dislake.delete()
    return redirect('posts:profile', username)
