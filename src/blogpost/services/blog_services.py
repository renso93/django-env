"""
Services pour la logique métier du blog.
"""
from ..models import BlogPost

def increment_view_count(blog_post):
    """Incrémente le compteur de vues d'un article."""
    blog_post.views += 1
    blog_post.save(update_fields=['views'])

def get_related_posts(blog_post, limit=3):
    """Retourne les articles liés par catégorie ou tags."""
    related = BlogPost.objects.filter(status='published')\
        .exclude(id=blog_post.id)\
        .filter(category=blog_post.category)\
        .order_by('-created_at')[:limit]
    return related

def get_popular_posts(limit=5):
    """Retourne les articles les plus vus."""
    return BlogPost.objects.filter(status='published')\
        .order_by('-views')[:limit]