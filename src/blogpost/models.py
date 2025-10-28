from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from PIL import Image

# Create your models here.
class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé étendant AbstractUser.
    Attributs supplémentaires:
        bio (str): Une courte biographie de l'utilisateur.
        location (str): La localisation de l'utilisateur.
        birth_date (date): La date de naissance de l'utilisateur.
        avatar (ImageField): Une image d'avatar pour l'utilisateur.

    """

    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg', blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.avatar:
            img = Image.open(self.avatar.path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
    

class BlogPost(models.Model):
    """Représentation du model blog post.
    Attributs:
        title (str): Le titre de l'article de blog.
        slug (str): Le slug unique pour l'URL de l'article.
        content (str): Le contenu principal de l'article.
        author (CustomUser): L'auteur de l'article, lié au modèle CustomUser.
        category (Category): La catégorie à laquelle appartient l'article.
        tags (ManyToManyField): Les tags associés à l'article.
        status (str): Le statut de l'article (brouillon, publié, archivé).
        featured_image (ImageField): L'image mise en avant pour l'article.
        created_at (DateTimeField): La date et l'heure de création de l'article.
        updated_at (DateTimeField): La date et l'heure de la dernière mise à jour de l'article.
        views (PositiveIntegerField): Le nombre de vues de l'article.
    """

    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL , blank=True, null=True, related_name='blog_posts')
    tags = models.ManyToManyField('Tag', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'status']),
                   models.Index(fields=['slug'])
                   ]
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blogpost_detail', kwargs={'slug': self.slug})

class Tag(models.Model):
    """
    Réprésentation du model Tag.
    Attributs:
        name (str): Le nom du tag.
        slug (str): Le slug unique pour l'URL du tag.
    """

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('tag_detail', kwargs={'slug': self.slug})