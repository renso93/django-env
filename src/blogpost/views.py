from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q
from django.utils.text import slugify
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import TemplateView

from .models import BlogPost, Category, Tag, CustomUser
from .forms import BlogPostForm, ContactForm
from .models import ContactMessage
from .services.blog_services import increment_view_count, get_related_posts, get_popular_posts
from .utils.text import generate_unique_slug, clean_html
from .utils.constants import POSTS_PER_PAGE, POST_STATUS

class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blogpost/blogpost_list.html'
    context_object_name = 'articles'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        queryset = BlogPost.objects.filter(status=POST_STATUS['PUBLISHED'])
        
        # Recherche
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        tag = self.request.GET.get('tag')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
        
        if category:
            queryset = queryset.filter(category__slug=category)
            
        if tag:
            queryset = queryset.filter(tags__slug=tag)
            
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context

class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blogpost/blogpost_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        # Récupère l'article et incrémente le compteur de vues
        obj = get_object_or_404(BlogPost, 
                              slug=self.kwargs['slug'],
                              status=POST_STATUS['PUBLISHED'])
        increment_view_count(obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        # Ajoute les articles liés par catégorie
        context['related_articles'] = get_related_posts(article)
        context['popular_posts'] = get_popular_posts(5)
        return context

class BlogPostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blogpost/blogpost_form.html'
    success_message = "L'article a été créé avec succès !"

    def form_valid(self, form):
        form.instance.author = self.request.user
        # Génère un slug unique à partir du titre
        form.instance.slug = generate_unique_slug(form.instance, form.instance.title, 'slug')
        return super().form_valid(form)

class BlogPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blogpost/blogpost_form.html'
    success_message = "L'article a été modifié avec succès !"

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff

    def form_valid(self, form):
        # Met à jour le slug si le titre a changé
        if form.instance.title != self.get_object().title:
            form.instance.slug = generate_unique_slug(form.instance, form.instance.title, 'slug')
        # Nettoie le contenu HTML
        form.instance.content = clean_html(form.instance.content)
        return super().form_valid(form)

class BlogPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = BlogPost
    template_name = 'blogpost/blogpost_confirm_delete.html'
    success_url = reverse_lazy('blogpost_list')
    success_message = "L'article a été supprimé avec succès !"

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

class CategoryListView(ListView):
    model = Category
    template_name = 'blogpost/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(ListView):
    """Liste paginée des articles d'une catégorie."""
    model = BlogPost
    template_name = 'blogpost/category_detail.html'
    context_object_name = 'blog_posts'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        # Filter posts by category slug provided in the URL
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=slug)
        return BlogPost.objects.filter(category=category, status=POST_STATUS['PUBLISHED']).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # include category for template header
        context['category'] = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context

class TagDetailView(ListView):
    """Liste paginée des articles pour un tag donné."""
    model = BlogPost
    template_name = 'blogpost/tag_detail.html'
    context_object_name = 'blog_posts'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        tag = get_object_or_404(Tag, slug=slug)
        return BlogPost.objects.filter(tags=tag, status=POST_STATUS['PUBLISHED']).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context


class DraftListView(LoginRequiredMixin, ListView):
    """Liste des brouillons. Les auteurs voient leurs brouillons ; le staff voit tous."""
    model = BlogPost
    template_name = 'blogpost/blogpost_draft_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        qs = BlogPost.objects.filter(status='draft')
        if not self.request.user.is_authenticated:
            # utilisateurs anonymes ne doivent pas voir les brouillons
            return BlogPost.objects.none()
        if self.request.user.is_staff:
            return qs.order_by('-created_at')
        return qs.filter(author=self.request.user).order_by('-created_at')


class ArchiveListView(ListView):
    """Liste des articles archivés (publics)."""
    model = BlogPost
    template_name = 'blogpost/blogpost_archive_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.filter(status='archived').order_by('-created_at')
    

class ContactCreateView(SuccessMessageMixin, CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'blogpost/contact_form.html'
    success_url = reverse_lazy('contact_thanks')
    success_message = "Merci ! Votre message a bien été envoyé."

    def form_valid(self, form):
        # Save the message
        response = super().form_valid(form)
        # Attempt to send a notification email if settings configured
        try:
            subject = form.cleaned_data.get('subject') or 'Nouveau message de contact'
            body = form.cleaned_data.get('message')
            sender = form.cleaned_data.get('email')
            site_from = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
            if site_from:
                send_mail(
                    subject,
                    f"De: {form.cleaned_data.get('name')} <{sender}>\n\n{body}",
                    site_from,
                    [site_from],
                    fail_silently=True,
                )
        except Exception:
            # Don't break the UX on email errors; message already saved.
            pass
        return response

    def get_context_data(self, **kwargs):
        # Add a small note for template about email backend in development
        context = super().get_context_data(**kwargs)
        backend = getattr(settings, 'EMAIL_BACKEND', '')
        # If console or locmem backend is used, show a short info to users
        context['email_backend_note'] = any(x in backend for x in ('console', 'locmem')) or getattr(settings, 'DEBUG', False)
        return context


class ContactThanksView(TemplateView):
    template_name = 'blogpost/contact_thanks.html'

