from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import BlogPost, CustomUser

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'category', 'tags', 'featured_image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError("Le titre doit contenir au moins 5 caractères.")
        return title
        

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


from .models import ContactMessage

# Optional reCAPTCHA support: only add the field if django-recaptcha is installed
# and project settings include RECAPTCHA_PUBLIC_KEY and RECAPTCHA_PRIVATE_KEY.
try:
    from captcha.fields import ReCaptchaField
    from captcha.widgets import ReCaptchaV2Checkbox
except Exception:
    # Some distributions expose the package as `django_recaptcha` instead of
    # `captcha` (module name differs). Try that as a fallback so the project
    # works with either distribution.
    try:
        from django_recaptcha.fields import ReCaptchaField
        from django_recaptcha.widgets import ReCaptchaV2Checkbox
    except Exception:
        ReCaptchaField = None

from django.conf import settings


def _try_get_recaptcha_field():
    """Attempt to import a ReCaptchaField and widget from installed packages.

    Return a tuple (field_class, widget_class) or (None, None) if not available.
    Import is performed lazily to avoid packages that touch Django settings at
    import time causing errors during test module import.
    """
    try:
        from captcha.fields import ReCaptchaField
        from captcha.widgets import ReCaptchaV2Checkbox
        return ReCaptchaField, ReCaptchaV2Checkbox
    except Exception:
        try:
            from django_recaptcha.fields import ReCaptchaField
            from django_recaptcha.widgets import ReCaptchaV2Checkbox
            return ReCaptchaField, ReCaptchaV2Checkbox
        except Exception:
            return None, None


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Honeypot field to limit spam bots (hidden in the template). Must be empty.
        if 'honeypot' not in self.fields:
            self.fields['honeypot'] = forms.CharField(required=False, widget=forms.HiddenInput)

        # Optional reCAPTCHA: add at instantiation time so override_settings in tests
        # can ensure RECAPTCHA_* keys are present when the form is constructed.
        if getattr(settings, 'RECAPTCHA_PUBLIC_KEY', None) and getattr(settings, 'RECAPTCHA_PRIVATE_KEY', None):
            FieldClass, WidgetClass = _try_get_recaptcha_field()
            if FieldClass and 'captcha' not in self.fields:
                self.fields['captcha'] = FieldClass(widget=WidgetClass())

    def clean_message(self):
        msg = self.cleaned_data.get('message', '')
        if len(msg) < 10:
            raise forms.ValidationError("Le message doit contenir au moins 10 caractères.")
        return msg

    def clean_honeypot(self):
        hp = self.cleaned_data.get('honeypot')
        if hp:
            raise forms.ValidationError("Spam détecté.")
        return hp
