from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import Category, BlogPost

CACHE_KEY = 'nav_categories'


@receiver(post_save, sender=Category)
def clear_nav_categories_on_save(sender, instance, **kwargs):
    """Clear nav categories cache when a category is saved or updated."""
    cache.delete(CACHE_KEY)


@receiver(post_delete, sender=Category)
def clear_nav_categories_on_delete(sender, instance, **kwargs):
    """Clear nav categories cache when a category is deleted."""
    cache.delete(CACHE_KEY)


@receiver(pre_save, sender=BlogPost)
def clear_nav_categories_on_blogpost_pre_save(sender, instance, **kwargs):
    """Clear nav categories cache when a blog post is created or when its category changes.

    Logic:
    - If instance.pk is falsy (new object), clear cache.
    - If existing object and category_id changed, clear cache.
    - Otherwise, do nothing to avoid unnecessary cache churn.
    """
    # New object -> clear cache
    if not instance.pk:
        cache.delete(CACHE_KEY)
        return

    try:
        old = BlogPost.objects.get(pk=instance.pk)
    except BlogPost.DoesNotExist:
        cache.delete(CACHE_KEY)
        return

    old_cat = getattr(old, 'category_id', None)
    new_cat = getattr(instance, 'category_id', None)
    if old_cat != new_cat:
        cache.delete(CACHE_KEY)


@receiver(post_delete, sender=BlogPost)
def clear_nav_categories_on_blogpost_delete(sender, instance, **kwargs):
    """Clear nav categories cache when a blog post is deleted."""
    cache.delete(CACHE_KEY)
