"""Utilitaires pour le blog."""

import re
from django.utils.text import slugify

def generate_unique_slug(model_instance, title, slug_field):
    """
    Génère un slug unique pour un modèle donné.
    
    Args:
        model_instance: Instance du modèle
        title: Titre à partir duquel générer le slug
        slug_field: Nom du champ slug dans le modèle
    
    Returns:
        str: Slug unique
    """
    slug = slugify(title)
    unique_slug = slug
    extension = 1

    model_class = model_instance.__class__
    while model_class.objects.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f'{slug}-{extension}'
        extension += 1
    
    return unique_slug

def clean_html(html_content):
    """
    Nettoie le contenu HTML des scripts et autres éléments dangereux.
    
    Args:
        html_content: Contenu HTML à nettoyer
    
    Returns:
        str: Contenu HTML nettoyé
    """
    # Supprime les balises script
    clean_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    
    # Supprime les gestionnaires d'événements on*
    clean_content = re.sub(r' on\w+="[^"]*"', '', clean_content)
    
    return clean_content