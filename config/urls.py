from django.contrib import admin
from django.urls import path, include, re_path # Добавили re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve # Добавили serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('forum.urls')),
    path('users/', include('users.urls')),
    path('achievements/', include('achievements.urls')),
]

# Вместо 'if settings.DEBUG', используем явную раздачу для локальных тестов
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Этот блок позволит видеть медиафайлы даже при DEBUG = False
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]

# Custom error handlers
handler404 = 'forum.views.custom_404'
handler500 = 'forum.views.custom_500'