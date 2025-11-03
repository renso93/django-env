from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Return a URL-encoded querystring with updated parameters.

    Usage in template:
        <a href="?{% url_replace page=2 %}">page 2</a>

    This preserves existing GET parameters and replaces/sets the provided ones.
    """
    request = context.get('request')
    if request is None:
        return ''
    params = request.GET.copy()
    for k, v in kwargs.items():
        params[k] = v
    # Remove any empty params
    for k in [k for k, val in params.items() if val == '' or val is None]:
        params.pop(k, None)
    return params.urlencode()