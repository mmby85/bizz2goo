from django import template

register = template.Library()

@register.filter
def first_words(value, num_words=50):
    """
    Returns the first 'num_words' words from the string.
    """
    words = value.split()  # Divise le texte en mots
    return ' '.join(words[:num_words]) + ('...' if len(words) > num_words else '')