from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count, Max
from .models import Category, Topic, Post
from .forms import TopicForm, PostForm
from achievements.utils import check_achievements
from config.forum_config import FORUM_CONFIG
from users.models import User

def index(request):
    categories = Category.objects.annotate(
        topic_count=Count('topics'),
        last_post_time=Max('topics__posts__created_at')
    )
    
    recent_topics = Topic.objects.select_related('author', 'category').order_by('-created_at')[:5]
    
    context = {
        'categories': categories,
        'recent_topics': recent_topics,
    }
    return render(request, 'forum/index.html', context)

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    topics_list = Topic.objects.filter(category=category).select_related('author').annotate(
        post_count=Count('posts'),
        last_post_time=Max('posts__created_at')
    )
    
    paginator = Paginator(topics_list, FORUM_CONFIG['items_per_page'])
    page = request.GET.get('page')
    topics = paginator.get_page(page)
    
    context = {
        'category': category,
        'topics': topics,
    }
    return render(request, 'forum/category_detail.html', context)

def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    topic.views += 1
    topic.save(update_fields=['views'])
    
    posts_list = topic.posts.select_related('author')
    paginator = Paginator(posts_list, FORUM_CONFIG['items_per_page'])
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    if request.method == 'POST' and request.user.is_authenticated:
        if topic.is_closed and request.user.role not in ['moderator', 'admin']:
            messages.error(request, 'Эта тема закрыта для обсуждения.')
            return redirect('forum:topic_detail', pk=pk)
        
        content = request.POST.get('content', '').strip()
        if content:
            post = Post.objects.create(
                topic=topic,
                author=request.user,
                content=content
            )
            check_achievements(request.user)
            messages.success(request, 'Сообщение добавлено!')
            return redirect('forum:topic_detail', pk=pk)
        else:
            messages.error(request, 'Сообщение не может быть пустым.')
    
    context = {
        'topic': topic,
        'posts': posts,
    }
    return render(request, 'forum/topic_detail.html', context)

@login_required
def create_topic(request, category_pk):
    category = get_object_or_404(Category, pk=category_pk)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        first_post = request.POST.get('first_post', '').strip()
        
        if not title or not first_post:
            messages.error(request, 'Заполните все поля.')
        else:
            topic = Topic.objects.create(
                category=category,
                title=title,
                author=request.user
            )
            
            post = Post.objects.create(
                topic=topic,
                author=request.user,
                content=first_post
            )
            
            check_achievements(request.user)
            messages.success(request, 'Тема создана!')
            return redirect('forum:topic_detail', pk=topic.pk)
    
    context = {
        'category': category,
    }
    return render(request, 'forum/create_topic.html', context)

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Проверка: только автор может редактировать в течение 30 минут
    if request.user != post.author:
        messages.error(request, 'Вы не можете редактировать это сообщение.')
        return redirect('forum:topic_detail', pk=post.topic.pk)
    
    from datetime import timedelta
    from django.utils import timezone
    time_limit = timezone.now() - timedelta(minutes=30)
    if post.created_at < time_limit:
        messages.error(request, 'Время редактирования истекло (30 минут).')
        return redirect('forum:topic_detail', pk=post.topic.pk)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            post.content = content
            post.is_edited = True
            post.save()
            messages.success(request, 'Сообщение обновлено!')
            return redirect('forum:topic_detail', pk=post.topic.pk)
        else:
            messages.error(request, 'Сообщение не может быть пустым.')
    
    # Явно передаем post в контекст
    return render(request, 'forum/edit_post.html', {'post': post})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    topic = post.topic
    
    # Проверка прав: автор или модератор/админ
    if request.user != post.author and request.user.role not in ['moderator', 'admin']:
        messages.error(request, 'Вы не можете удалить это сообщение.')
        return redirect('forum:topic_detail', pk=topic.pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Сообщение удалено!')
        
        if not topic.posts.exists():
            topic.delete()
            return redirect('forum:category_detail', pk=topic.category.pk)
        
        return redirect('forum:topic_detail', pk=topic.pk)
    
    return render(request, 'forum/delete_post.html', {'post': post})

@login_required
def close_topic(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    
    if request.user.role not in ['moderator', 'admin']:
        messages.error(request, 'У вас нет прав для этого действия.')
        return redirect('forum:topic_detail', pk=pk)
    
    topic.is_closed = not topic.is_closed
    topic.save()
    
    status = 'закрыта' if topic.is_closed else 'открыта'
    messages.success(request, f'Тема {status}!')
    return redirect('forum:topic_detail', pk=pk)

@login_required
def moderator_panel(request):
    if request.user.role not in ['moderator', 'admin']:
        messages.error(request, 'У вас нет доступа к панели модератора.')
        return redirect('forum:index')
    
    # Статистика
    total_topics = Topic.objects.count()
    total_posts = Post.objects.count()
    total_users = User.objects.count()
    
    # Последние сообщения
    recent_posts = Post.objects.select_related('author', 'topic').order_by('-created_at')[:20]
    
    # Последние темы
    recent_topics = Topic.objects.select_related('author', 'category').order_by('-created_at')[:10]
    
    context = {
        'total_topics': total_topics,
        'total_posts': total_posts,
        'total_users': total_users,
        'recent_posts': recent_posts,
        'recent_topics': recent_topics,
    }
    return render(request, 'forum/moderator_panel.html', context)

def custom_404(request, exception=None):
    """Custom 404 page"""
    return render(request, '404.html', status=404)

def custom_500(request):
    """Custom 500 page"""
    return render(request, '500.html', status=500)