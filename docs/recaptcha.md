## reCAPTCHA — installation et configuration

Cette application propose un support optionnel pour Google reCAPTCHA (via `django-recaptcha`).
L'intégration est conditionnelle : si le paquet `django-recaptcha` est installé et que les clés
`RECAPTCHA_PUBLIC_KEY` et `RECAPTCHA_PRIVATE_KEY` sont définies dans vos settings, le champ
`captcha` sera ajouté au formulaire de contact (`ContactForm`). Sinon le formulaire fonctionne sans.

Étapes d'installation :

1. Installer la dépendance :

```bash
pip install django-recaptcha
```

2. Ajouter à `requirements.txt` (optionnel) :

```
django-recaptcha
```

3. Configurer vos clés (dans `settings/developpement.py` pour le dev, et dans `settings/production.py` pour la prod) :

```py
RECAPTCHA_PUBLIC_KEY = 'votre-site-key'
RECAPTCHA_PRIVATE_KEY = 'votre-secret-key'
# éventuellement
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
```

4. Obtenir vos clés sur https://www.google.com/recaptcha/admin

5. Le formulaire de contact utilisera alors le widget reCAPTCHA et validera le token
   côté serveur via le package.

Remarques
- Le code de l'application ajoute le champ `captcha` uniquement si la dépendance
  et les clés sont présentes, de sorte que l'environnement de test ou de développement
  qui ne possède pas ces clés continuera à fonctionner.
- Pour tester en local, vous pouvez utiliser les clefs de test Google ou configurer
  `SILENCED_SYSTEM_CHECKS` comme indiqué.
