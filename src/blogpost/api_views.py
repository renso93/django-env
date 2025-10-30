from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend

from .api_filters import BlogPostFilter

from .models import BlogPost, Category, Tag
from .serializers import BlogPostSerializer, CategorySerializer, TagSerializer
from .api_permissions import IsAuthorOrReadOnly


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all().order_by('-created_at')
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    # Use SearchFilter and DjangoFilterBackend with our explicit FilterSet
    # that uses CharFilter for slug lookups. This avoids automatic
    # ModelChoiceFilter generation while keeping django-filter's API.
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'content']
    filterset_class = BlogPostFilter

    def get_queryset(self):
        qs = super().get_queryset()
        # By default, unauthenticated users should only see published posts
        if not self.request.user.is_authenticated:
            qs = qs.filter(status='published')
        else:
            # Allow staff to see all, authors see their own plus published
            if not self.request.user.is_staff:
                qs = qs.filter(models.Q(status='published') | models.Q(author=self.request.user))
        # support filtering by category or tag via query params
        category = self.request.query_params.get('category')
        tag = self.request.query_params.get('tag')
        if category:
            qs = qs.filter(category__slug=category)
        if tag:
            qs = qs.filter(tags__slug=tag)
        return qs.distinct()

    def perform_create(self, serializer):
        # set author automatically
        serializer.save(author=self.request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
