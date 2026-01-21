from .forum_config import FORUM_CONFIG

def forum_config(request):
    return {'FORUM_CONFIG': FORUM_CONFIG}