from django.urls import path

from . import views

urlpatterns = [
    path("", views.BlogPostListView.as_view(), name="article_list"),
    path("article/<slug:slug>/", views.BlogPostDetailView.as_view(), name="article_detail"),
    path("create/", views.BlogPostCreateView.as_view(), name="article_create"),
    path("article/<slug:slug>/edit/", views.BlogPostUpdateView.as_view(), name="article_edit"),
]
