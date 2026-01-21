from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import secrets
from .models import User, PasswordResetToken
from .forms import RegistrationForm, LoginForm, ProfileForm, PasswordResetRequestForm, PasswordResetForm
from achievements.models import UserAchievement

def register(request):
    if request.user.is_authenticated:
        return redirect('forum:index')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('forum:index')
    else:
        form = RegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('forum:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user:
                login(request, user)
                next_url = request.GET.get('next', 'forum:index')
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный логин или пароль.')
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('forum:index')

def profile(request, username):
    user = get_object_or_404(User, username=username)
    achievements = UserAchievement.objects.filter(user=user).select_related('achievement')
    recent_posts = user.posts.select_related('topic').order_by('-created_at')[:5]
    recent_topics = user.topics.select_related('category').order_by('-created_at')[:5]
    
    context = {
        'profile_user': user,
        'achievements': achievements,
        'recent_posts': recent_posts,
        'recent_topics': recent_topics,
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        avatar = request.FILES.get('avatar')
        
        request.user.bio = bio
        if avatar:
            request.user.avatar = avatar
        request.user.save()
        
        messages.success(request, 'Профиль обновлен!')
        return redirect('users:profile', username=request.user.username)
    
    return render(request, 'users/edit_profile.html')

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = secrets.token_urlsafe(32)
                
                PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
                PasswordResetToken.objects.create(user=user, token=token)
                
                reset_url = request.build_absolute_uri(
                    reverse('users:password_reset_confirm', kwargs={'token': token})
                )
                
                send_mail(
                    'Восстановление пароля',
                    f'Для восстановления пароля перейдите по ссылке: {reset_url}\n\nСсылка действительна 24 часа.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Инструкции отправлены на email!')
                return redirect('users:login')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'users/password_reset_request.html', {'form': form})

def password_reset_confirm(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if not reset_token.is_valid():
            messages.error(request, 'Ссылка недействительна или устарела.')
            return redirect('users:password_reset_request')
        
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                reset_token.user.set_password(form.cleaned_data['password'])
                reset_token.user.save()
                reset_token.used = True
                reset_token.save()
                
                messages.success(request, 'Пароль успешно изменен!')
                return redirect('users:login')
        else:
            form = PasswordResetForm()
        
        return render(request, 'users/password_reset_confirm.html', {'form': form})
    
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Недействительная ссылка.')
        return redirect('users:password_reset_request')