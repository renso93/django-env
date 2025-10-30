import django_filters

from .models import BlogPost


class BlogPostFilter(django_filters.FilterSet):
    """Custom FilterSet using CharFilter for slug lookups to avoid
    django-filter model choice fields which caused compatibility issues
    in the test environment.
    """
    # Explicitly define each filter as CharFilter to avoid automatic
    # generation of Choice/ModelChoice filters which can trigger form
    # construction issues in some environments.
    category = django_filters.CharFilter(field_name='category__slug')
    tag = django_filters.CharFilter(field_name='tags__slug')
    status = django_filters.CharFilter(field_name='status')
    author = django_filters.CharFilter(field_name='author__username')

    class Meta:
        model = BlogPost
        # We declare explicit filter attributes above; list the exposed names.
        fields = ['status', 'author', 'category', 'tag']


from rest_framework.filters import BaseFilterBackend


class SimpleQueryFilterBackend(BaseFilterBackend):
    """A tiny, explicit filter backend that applies a few query-param filters
    without relying on django-filter's form machinery. This avoids the
    compatibility issues seen in tests while keeping filter behavior clear.
    Supported query params:
      - category: slug of category
      - tag: slug of tag
      - status: status value
      - author: author's username
    """

    def filter_queryset(self, request, queryset, view):
        params = request.query_params
        category = params.get('category')
        tag = params.get('tag')
        status_val = params.get('status')
        author = params.get('author')

        if category:
            queryset = queryset.filter(category__slug=category)
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        if status_val:
            queryset = queryset.filter(status=status_val)
        if author:
            queryset = queryset.filter(author__username=author)
        return queryset.distinct()
