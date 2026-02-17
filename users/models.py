from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.username
    
    def get_post_count(self):
        return self.posts.count()
    
    def get_topic_count(self):
        return self.topics.count()

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    used = models.BooleanField(default=False)
    
    def is_valid(self):
        from datetime import timedelta
        return not self.used and (timezone.now() - self.created_at) < timedelta(hours=24)

class UserBlock(models.Model):
    """Модель для блокировки пользователя от отправки сообщений"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocks')
    blocked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blocks_given')
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    blocked_until = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} заблокирован до {self.blocked_until}'
    
    def is_active(self):
        """Проверить, активна ли блокировка"""
        return timezone.now() < self.blocked_until
    
    def get_remaining_time(self):
        """Получить оставшееся время блокировки"""
        if self.is_active():
            remaining = self.blocked_until - timezone.now()
            return remaining
        return None