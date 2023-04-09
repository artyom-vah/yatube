from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from posts.utils import paginator_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

User = get_user_model()


def index(request):
    posts = Post.objects.select_related('author', 'group')
    page_obj = paginator_page(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.related_posts_in_group.all()
    page_obj = paginator_page(request, posts)
    context = {
        'posts': posts,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.related_author_of_posts.all()
    page_obj = paginator_page(request, posts)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    context = {
        'author': author,
        'posts': posts,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related(
        'author', 'group'), id=post_id
    )
    form_comment = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'form_comment': form_comment,
        'comments': comments,
    }
    # print('get_object_or_404(Post, pk=post_id)',
    #       get_object_or_404(Post, pk=post_id))
    # print('CommentForm()', CommentForm())
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        print('PostForm(request.POST or None)', PostForm(request.POST or None))
        return redirect('posts:profile', post.author)
    return render(
        request, 'posts/create_post.html', {'form': form}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


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


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_page(request, posts)
    context = {
        'page_obj': page_obj,
        'follow': True,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != request.user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
