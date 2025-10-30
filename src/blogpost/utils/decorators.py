"""Décorateurs personnalisés pour les vues."""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def author_required(view_func):
    """
    Vérifie que l'utilisateur est l'auteur de l'objet.
    À utiliser sur les vues de détail/modification d'articles.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        obj = view_func(request, *args, **kwargs)
        if hasattr(obj, 'author') and obj.author != request.user:
            messages.error(request, "Vous n'avez pas la permission de modifier cet article.")
            return redirect('blogpost_list')
        return obj
    return wrapper

def staff_or_author_required(view_func):
    """
    Vérifie que l'utilisateur est staff ou l'auteur de l'objet.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        obj = view_func(request, *args, **kwargs)
        if not request.user.is_staff and (not hasattr(obj, 'author') or obj.author != request.user):
            messages.error(request, "Accès non autorisé.")
            return redirect('blogpost_list')
        return obj
    return wrapper