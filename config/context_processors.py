from forum.models import ForumConfig
from .forum_config import FORUM_CONFIG as DEFAULT_CONFIG

def forum_config(request):
    """Получить конфиг форума из БД или использовать дефолтный"""
    try:
        config = ForumConfig.get_config()
        return {'FORUM_CONFIG': config}
    except:
        # Fallback на словарь если БД недоступна
        return {'FORUM_CONFIG': DEFAULT_CONFIG}