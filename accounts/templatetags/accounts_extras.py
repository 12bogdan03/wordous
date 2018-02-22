from django import template


register = template.Library()


@register.filter
def is_worker(user):
    return user.groups.filter(name='Worker').exists()


@register.filter
def is_client(user):
    return user.groups.filter(name='Client').exists()
