"""Services pour la gestion des utilisateurs."""

from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(user):
    """Envoie un email de bienvenue à un nouvel utilisateur."""
    subject = 'Bienvenue sur notre blog !'
    message = f'Bonjour {user.username},\n\nMerci de vous être inscrit sur notre blog.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    send_mail(subject, message, from_email, recipient_list)