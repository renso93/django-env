try:
    from django_recaptcha.widgets import ReCaptchaV2Checkbox
except Exception:
    # Minimal stub widget when package not fully available during import.
    class ReCaptchaV2Checkbox:
        def __init__(self, *args, **kwargs):
            pass
