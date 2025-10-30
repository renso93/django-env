## API — usage rapide

Endpoints principaux

- `GET /api/posts/` — liste des articles
- `POST /api/posts/` — création d'un article (auth requis)
- `GET /api/posts/{id}/` — détail d'un article
- `PATCH /api/posts/{id}/` / `PUT /api/posts/{id}/` — mise à jour (seul l'auteur)
- `DELETE /api/posts/{id}/` — suppression (seul l'auteur)
- `GET /api/categories/` — liste des catégories
- `GET /api/tags/` — liste des tags

## Filtrage et recherche

Par souci de simplicité et compatibilité, le backend utilise le filtre manuel suivant :

- Filtrer par catégorie (slug) :
  - Exemple : `GET /api/posts/?category=mes-articles`
- Filtrer par tag (slug) :
  - Exemple : `GET /api/posts/?tag=django`
- Recherche plein texte (titre + contenu) via DRF SearchFilter :
  - Exemple : `GET /api/posts/?search=redis`

Vous pouvez combiner ces paramètres :

`GET /api/posts/?category=mes-articles&tag=django&search=cache`

Remarques :
- Les articles non publiés ne sont visibles que par leur auteur (ou le staff). Les utilisateurs non authentifiés ne verront que les articles publiés.
- Les paramètres `category` et `tag` attendent le slug (chaîne), pas l'id.

## Création / mise à jour d'un article (exemples)

POST /api/posts/ (JSON) — création (l'auteur est pris depuis l'utilisateur authentifié)

{
  "title": "Mon article",
  "content": "Contenu...",
  "category": "mon-slug-de-categorie",
  "tags": ["tag1", "tag2"]
}

Réponse attendue : 201 Created et représentation JSON du post.

PATCH /api/posts/{id}/ (JSON) — modification partielle

{
  "title": "Titre modifié"
}

Permissions : seuls les auteurs peuvent modifier/supprimer leur article. Les requêtes non authentifiées reçoivent 401 pour POST/PATCH/DELETE.

## Pourquoi django-filter n'est pas activé ici

Pendant l'intégration, l'usage par défaut de `DjangoFilterBackend` a provoqué des erreurs de construction de formulaires dans l'environnement de tests (incompatibilité avec certains types de champs pour les filtres sur des slugs). Pour rester stable et explicite, l'API :

- conserve `SearchFilter` pour la recherche,
- applique un filtrage manuel via `?category=` et `?tag=` dans la méthode `get_queryset()` de la viewset.

Si vous préférez réactiver `django-filter`, deux options sûres :

1) Fournir un `FilterSet` explicite qui utilise `CharFilter` pour les champs slug, par exemple :

```py
import django_filters

class BlogPostFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    tag = django_filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = BlogPost
        fields = ['status', 'author__username', 'category', 'tag']
```

puis référencer `filterset_class = BlogPostFilter` dans la `BlogPostViewSet` et réactiver `DjangoFilterBackend`.

2) Mettre à jour la version de `django-filter` pour une version compatible avec votre pile (tester d'abord sur l'environnement de CI/local), puis réactiver `DjangoFilterBackend`.

## Exemples curl rapides

Lister publiés + recherche :

```bash
curl -s "http://localhost:8000/api/posts/?search=redis" | jq .
```

Créer (avec token d'API) :

```bash
curl -X POST -H "Authorization: Token <VOTRE_TOKEN>" -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"ok","category":"tech","tags":["django"]}' \
  http://localhost:8000/api/posts/
```

## Notes finales
- Les endpoints acceptent et renvoient les slugs pour catégories et tags (API conviviale pour les clients).
- Si vous voulez, je peux :
  - ajouter le `FilterSet` et réactiver `DjangoFilterBackend` (option sûre : CharFilter),
  - ou lancer la suite de tests complète pour valider l'absence de régressions.

---
Fichier généré automatiquement : documentation d'usage pour l'API posts.
