from django.contrib import admin
from .models import BlogPost, Category

# Register your models here.
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    pass