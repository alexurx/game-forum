from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserBlock

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'avatar', 'bio')}),
    )

@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ['user', 'blocked_by', 'created_at', 'blocked_until', 'is_active']
    list_filter = ['created_at', 'blocked_until']
    search_fields = ['user__username', 'blocked_by__username']
    readonly_fields = ['created_at']
    
    def is_active(self, obj):
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = 'Активна'