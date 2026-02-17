from django.db import models
from django.utils import timezone
from django.urls import reverse
from users.models import User

class ForumConfig(models.Model):
    """Глобальная конфигурация форума"""
    name = models.CharField(max_length=100, default='Forum')
    logo_text = models.CharField(max_length=100, blank=True)
    logo_image = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name='Логотип (картинка)')
    description = models.TextField(blank=True)
    game_title = models.CharField(max_length=100, blank=True)
    icon = models.CharField(max_length=10, default='🎮')
    primary_color = models.CharField(max_length=7, default='#4E1260')
    secondary_color = models.CharField(max_length=7, default='#0f1923')
    meta_description = models.TextField(blank=True)
    items_per_page = models.IntegerField(default=20)
    
    class Meta:
        verbose_name = 'Forum Configuration'
        verbose_name_plural = 'Forum Configuration'
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_config(cls):
        """Получить конфиг или создать дефолтный"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def get_topic_count(self):
        return self.topics.count()
    
    def get_post_count(self):
        return sum(topic.posts.count() for topic in self.topics.all())

class Topic(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    cover_image = models.ImageField(upload_to='topic_covers/', blank=True, null=True, verbose_name='Обложка темы')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('forum:topic_detail', kwargs={'pk': self.pk})
    
    def get_post_count(self):
        return self.posts.count()
    
    def get_last_post(self):
        return self.posts.order_by('-created_at').first()

class Post(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Post by {self.author.username} in {self.topic.title}'