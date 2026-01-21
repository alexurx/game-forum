from django.contrib import admin
from .models import Category, Topic, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'created_at']
    list_editable = ['order']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_pinned', 'is_closed', 'created_at']
    list_filter = ['category', 'is_pinned', 'is_closed']
    search_fields = ['title', 'author__username']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['topic', 'author', 'created_at', 'is_edited']
    list_filter = ['created_at', 'is_edited']
    search_fields = ['content', 'author__username']