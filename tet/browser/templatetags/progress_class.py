from django import template

register = template.Library()

# Usage: {% progress_class {number} %}
@register.simple_tag(name='progress_class')
def do_progress_class(progress):

    progress_class = ''

    if progress < 35:
        progress_class = 'progress-bar-very-poor'

    elif progress < 55:
        progress_class = 'progress-bar-poor'

    elif progress < 75:
        progress_class = 'progress-bar-fair'

    elif progress < 95:
        progress_class = 'progress-bar-good'

    elif progress >= 95:
        progress_class = 'progress-bar-very-good'

    return str(progress) + ' ' + progress_class
