from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('topic/<int:pk>/', views.topic_detail, name='topic_detail'),
    path('category/<int:category_pk>/create-topic/', views.create_topic, name='create_topic'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('topic/<int:pk>/close/', views.close_topic, name='close_topic'),
    path('moderator/', views.moderator_panel, name='moderator_panel'),
    path('user/<int:user_id>/block/', views.block_user, name='block_user'),
    path('user/<int:user_id>/unblock/', views.unblock_user, name='unblock_user'),
]