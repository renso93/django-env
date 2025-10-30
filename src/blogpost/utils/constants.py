# -*- coding: utf-8 -*-
"""Constants utilisées dans l'application blog."""

# Choix de statuts pour les articles
POST_STATUS = {
    'DRAFT': 'draft',
    'PUBLISHED': 'published',
    'ARCHIVED': 'archived'
}

# Configuration des images
IMAGE_SIZES = {
    'THUMBNAIL': (300, 300),
    'MEDIUM': (800, 600),
    'LARGE': (1200, 900)
}

# Pagination et limites
POSTS_PER_PAGE = 10
MAX_POSTS_PER_PAGE = 50
MAX_TITLE_LENGTH = 200
MAX_CONTENT_LENGTH = 50000  # 50KB de texte
MIN_CONTENT_LENGTH = 50     # Minimum 50 caractères

# Cache
CACHE_TTL = {
    'CATEGORY_LIST': 3600,  # 1 heure
    'POPULAR_POSTS': 1800,  # 30 minutes
    'TAG_CLOUD': 3600       # 1 heure
}