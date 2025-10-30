from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import api_views

router = DefaultRouter()
router.register(r'posts', api_views.BlogPostViewSet, basename='api-posts')
router.register(r'categories', api_views.CategoryViewSet, basename='api-categories')
router.register(r'tags', api_views.TagViewSet, basename='api-tags')

urlpatterns = [
    path('', include(router.urls)),
]
