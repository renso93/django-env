from django.urls import path

from . import views

#app_name = "blogpost"
urlpatterns = [
    path("", views.BlogPostListView.as_view(), name="blogpost_list"),
    path("article/<slug:slug>/", views.BlogPostDetailView.as_view(), name="blogpost_detail"),
    path("create/", views.BlogPostCreateView.as_view(), name="blogpost_create"),
    path("article/<slug:slug>/edit/", views.BlogPostUpdateView.as_view(), name="blogpost_edit"),
]
