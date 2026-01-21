from .models import Achievement, UserAchievement
from forum.models import Post, Topic

def check_achievements(user):
    """Проверяет и выдает пользователю заслуженные ачивки"""
    achievements = Achievement.objects.all()
    earned_achievements = []
    
    for achievement in achievements:
        if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            continue
        
        earned = False
        
        if achievement.requirement_type == 'first_post':
            if user.get_post_count() >= 1:
                earned = True
        
        elif achievement.requirement_type == 'first_topic':
            if user.get_topic_count() >= 1:
                earned = True
        
        elif achievement.requirement_type == 'post_count':
            if user.get_post_count() >= achievement.requirement_value:
                earned = True
        
        elif achievement.requirement_type == 'topic_count':
            if user.get_topic_count() >= achievement.requirement_value:
                earned = True
        
        elif achievement.requirement_type == 'popular_topic':
            user_topics = Topic.objects.filter(author=user)
            for topic in user_topics:
                if topic.get_post_count() >= achievement.requirement_value:
                    earned = True
                    break
        
        if earned:
            UserAchievement.objects.create(user=user, achievement=achievement)
            earned_achievements.append(achievement)
    
    return earned_achievements