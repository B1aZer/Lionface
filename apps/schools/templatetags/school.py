import datetime
from django import template

register = template.Library()


@register.assignment_tag(takes_context=True)
def school_years(context, start=2000):
    return reversed(range(start, datetime.date.today().year))
