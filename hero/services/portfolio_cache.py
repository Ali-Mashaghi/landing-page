from django.core.cache import cache

PROFILE_KEY = 'portfolio:profile'
PROJECTS_KEY = 'portfolio:projects'
SKILLS_KEY = 'portfolio:skills'

PORTFOLIO_KEYS = (PROFILE_KEY, PROJECTS_KEY, SKILLS_KEY)

DEFAULT_TIMEOUT = 300


def get_json(key):
    return cache.get(key)


def set_json(key, data, timeout=DEFAULT_TIMEOUT):
    cache.set(key, data, timeout)


def invalidate_portfolio():
    cache.delete_many(list(PORTFOLIO_KEYS))
