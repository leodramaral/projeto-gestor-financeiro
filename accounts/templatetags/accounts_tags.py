from django import template

register = template.Library()


@register.filter
def initials(name):
    """First letter of the first two words of `name`, uppercased ("" for an empty name)."""
    return "".join(word[0] for word in (name or "").split()[:2]).upper()
