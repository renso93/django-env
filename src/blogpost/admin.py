from django.contrib import admin
from .models import BlogPost, Category

# Register your models here.
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    pass

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'read_badge')
    list_filter = ('read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')

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