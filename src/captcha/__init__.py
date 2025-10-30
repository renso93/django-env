# Shim package to provide a `captcha` import for environments where
# the installed reCAPTCHA library exposes itself as `django_recaptcha`.
# This allows tests and code that import `captcha.fields` to work.
__all__ = ["fields", "widgets"]
