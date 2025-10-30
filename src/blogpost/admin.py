from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from .models import BlogPost, Category, Tag, ContactMessage, CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'avatar', 'bio', 'location', 'birth_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'post_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='Articles')
    def post_count(self, obj):
        """Return le nombre d'articles dans la catégorie."""
        return obj.blog_posts.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='Articles')
    def post_count(self, obj):
        """Return le nombre d'articles avec ce tag."""
        return obj.blogpost_set.count()


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at', 'views', 'get_tags')
    list_filter = ('status', 'category', 'author', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'category__name', 'tags__name')
    readonly_fields = ('created_at', 'updated_at', 'views', 'slug')
    autocomplete_fields = ['author', 'category', 'tags']

    @admin.display(description='Vues')
    def views(self, obj):
        """Affiche le nombre de vues de l'article."""
        return obj.views
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'content', 'featured_image')
        }),
        ('Relations', {
            'fields': ('author', 'category', 'tags')
        }),
        ('Publication', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
        ('Statistiques', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_published', 'make_draft']
    
    @admin.action(description="Publier les articles sélectionnés")
    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f"{updated} article(s) marqué(s) comme publié(s).")
    
    @admin.action(description="Mettre en brouillon les articles sélectionnés")
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f"{updated} article(s) mis en brouillon.")
    
    @admin.display(description='Tags')
    def get_tags(self, obj):
        """Return a comma-separated list of tag names."""
        return ", ".join(t.name for t in obj.tags.all())

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'read_badge', 'mark_read_link')
    list_filter = ('read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)

    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description="Marquer les messages sélectionnés comme lus")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(read=True)
        self.message_user(request, f"{updated} message(s) marqués comme lus.")

    @admin.action(description="Marquer les messages sélectionnés comme non lus")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(read=False)
        self.message_user(request, f"{updated} message(s) marqués comme non lus.")

    # Add a small help text in the admin change list via the changelist_view context
    def changelist_view(self, request, extra_context=None):
        extra = extra_context or {}
        extra['help_text'] = (
            "Sélectionnez un ou plusieurs messages puis utilisez l'action '"
            "Marquer les messages sélectionnés comme lus' pour marquer comme lus."
        )
        return super().changelist_view(request, extra_context=extra)

    # Add a toggle URL and a small button in the change form to mark an item read/unread
    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        my_urls = [
            path('<int:pk>/toggle_read/', self.admin_site.admin_view(self.toggle_read_view), name='blogpost_contactmessage_toggle_read'),
        ]
        return my_urls + urls

    def toggle_read_view(self, request, pk, *args, **kwargs):
        from django.shortcuts import redirect, get_object_or_404
        obj = get_object_or_404(ContactMessage, pk=pk)
        obj.read = not obj.read
        obj.save()
        msg = 'marqué comme lu' if obj.read else 'marqué comme non lu'
        self.message_user(request, f"Le message a été {msg}.")
        # Redirect back to the change page
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        from django.urls import reverse
        return redirect(reverse('admin:blogpost_contactmessage_changelist'))

    @admin.display(description='Action')
    def mark_read_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if not obj.pk:
            return ''
        url = reverse('admin:blogpost_contactmessage_toggle_read', args=[obj.pk])
        label = 'Marquer comme non lu' if obj.read else 'Marquer comme lu'
        # add a js-target class and data-pk for AJAX handling
        return format_html('<a class="button cm-toggle" href="{}" data-pk="{}">{}</a>', url, obj.pk, label)

    # Show the button in the change form and in readonly fields
    readonly_fields = ('created_at', 'mark_read_link')
    fields = ('name', 'email', 'subject', 'message', 'created_at', 'read', 'mark_read_link')

    @admin.display(description='Statut', ordering='read')
    def read_badge(self, obj):
        """Return an HTML badge (icon) for read/unread status."""
        from django.utils.html import format_html
        if obj.read:
            return format_html('<span class="cm-badge cm-badge-read" title="Lu">✓</span>')
        return format_html('<span class="cm-badge cm-badge-unread" title="Non lu">✕</span>')

    class Media:
        css = {
            'all': (
                'blogpost/admin/contactmessage.css',
            )
        }