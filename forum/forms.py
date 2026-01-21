from django import forms
from .models import Topic, Post

class TopicForm(forms.ModelForm):
    first_post = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8}),
        label='Первое сообщение'
    )
    
    class Meta:
        model = Topic
        fields = ['title']
        labels = {
            'title': 'Название темы',
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }
        labels = {
            'content': 'Сообщение',
        }