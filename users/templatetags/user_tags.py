from django import template

register = template.Library()


@register.inclusion_tag('users/partials/admin_badge.html')
def admin_badge(user):
    """Display admin badge if user is a superuser."""
    return {'user': user, 'is_admin': user.is_superuser if user else False}


@register.filter
def is_admin(user):
    """Check if user is an admin/superuser."""
    return user.is_superuser if user else False
