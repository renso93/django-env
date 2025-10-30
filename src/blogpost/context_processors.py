from .models import Category
from django.core.cache import cache


def nav_categories(request):
    """Return a small list of categories for navbar dropdown, cached for 1 hour."""
    cache_key = 'nav_categories'
    cats = cache.get(cache_key)
    if cats is None:
        cats = list(Category.objects.all()[:8])
        # store for 1 hour (3600s)
        cache.set(cache_key, cats, 3600)
    return {'nav_categories': cats}