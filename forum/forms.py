from django import forms
from .models import Topic, Post
from users.models import UserBlock

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

class UserBlockForm(forms.ModelForm):
    TIME_UNIT_CHOICES = [
        ('minutes', 'Минуты'),
        ('hours', 'Часы'),
        ('days', 'Дни'),
    ]
    
    block_duration = forms.IntegerField(
        min_value=1,
        label='Длительность блокировки',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите число'})
    )
    
    time_unit = forms.ChoiceField(
        choices=TIME_UNIT_CHOICES,
        label='Единица времени',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = UserBlock
        fields = ['reason']
        labels = {
            'reason': 'Причина блокировки',
        }
        widgets = {
            'reason': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Введите причину блокировки...'
            }),
        }