from django.shortcuts import render
from .models import Achievement

def achievement_list(request):
    achievements = Achievement.objects.all()
    context = {
        'achievements': achievements,
    }
    return render(request, 'achievements/list.html', context)