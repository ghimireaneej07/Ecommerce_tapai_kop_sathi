from django import template

register = template.Library()

PLACEHOLDER_MAP = {
    "tea": "images/placeholders/tea.svg",
    "coffee": "images/placeholders/coffee.svg",
    "herb": "images/placeholders/herbs.svg",
    "herbal": "images/placeholders/herbs.svg",
    "cream": "images/placeholders/cream.svg",
    "cosmetic": "images/placeholders/cosmetics.svg",
    "ladies": "images/placeholders/ladies.svg",
    "gent": "images/placeholders/gents.svg",
    "men": "images/placeholders/gents.svg",
    "women": "images/placeholders/ladies.svg",
}


@register.filter(name="placeholder_image")
def placeholder_image(category):
    if not category:
        return "images/placeholders/default.svg"

    name = ""
    slug = ""
    try:
        name = (category.name or "").lower()
        slug = (category.slug or "").lower()
    except Exception:
        name = str(category).lower()

    haystack = f"{name} {slug}"
    for key, value in PLACEHOLDER_MAP.items():
        if key in haystack:
            return value

    return "images/placeholders/default.svg"


@register.filter(name="category_label")
def category_label(category):
    if not category:
        return "Wellness"

    try:
        name = category.name
    except Exception:
        name = str(category)

    return name or "Wellness"
