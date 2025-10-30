from django.apps import AppConfig


class BlogpostConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blogpost"
    
    def ready(self):
        # Import signals to ensure they are registered when the app is ready
        try:
            import blogpost.signals  # noqa: F401
        except Exception:
            pass
