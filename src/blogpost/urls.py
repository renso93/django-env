from django.urls import path
from . import views

# app_name = "blogpost"
urlpatterns = [
    path("", views.BlogPostListView.as_view(), name="blogpost_list"),
    path("article/<slug:slug>/", views.BlogPostDetailView.as_view(), name="blogpost_detail"),
    path("create/", views.BlogPostCreateView.as_view(), name="blogpost_create"),
    path("article/<slug:slug>/edit/", views.BlogPostUpdateView.as_view(), name="blogpost_edit"),
    path("article/<slug:slug>/delete/", views.BlogPostDeleteView.as_view(), name="blogpost_delete"),

    # Category & Tag
    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("tag/<slug:slug>/", views.TagDetailView.as_view(), name="tag_detail"),

    # Drafts (my drafts and staff can view all) and Archives
    path("drafts/", views.DraftListView.as_view(), name="blogpost_drafts"),
    path("archives/", views.ArchiveListView.as_view(), name="blogpost_archives"),
    # Contact
    path('contact/', views.ContactCreateView.as_view(), name='contact'),
    path('contact/thanks/', views.ContactThanksView.as_view(), name='contact_thanks'),
]
