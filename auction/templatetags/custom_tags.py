from django import template

register = template.Library()

@register.filter(name='in_group')
def in_group(user, group_names):
    if hasattr(user, 'userprofile'):
        return user.userprofile.user_type in group_names.split(',')
    return False
