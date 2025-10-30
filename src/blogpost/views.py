from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q

from .models import BlogPost, Category
from .forms import BlogPostForm

# Create your views here.
class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blogpost/blogpost_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='published')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
        return queryset
    

class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blogpost/blogpost_detail.html'
    context_object_name = 'article'

    def get_object(self):
        obj = get_object_or_404(BlogPost, slug=self.kwargs['slug'], status= 'published')
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj


class BlogPostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BlogPost
    from_class = BlogPostForm
    template_name = 'blogpost/blogpost_form.html'
    success_message = "Article créé avec succès!"

    def form_valid(self, form):
        form.instance.author =  self.request.user
        return super().form_valid(form)


class BlogPostUpdateView(UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blogpost/blogpost_form.html'

    def tes_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff
    
