import datetime
from django import template

from schools.models import Alum

register = template.Library()


@register.assignment_tag()
def school_years(start=2000):
    return reversed(range(start, datetime.date.today().year + 1))


@register.assignment_tag()
def alum_from_school(profile, year, school):
    try:
        alum = Alum.objects.get(user=profile, year=year, school=school)
        return alum
    except Alum.DoesNotExist:
        return None


@register.assignment_tag()
def year_finish_school(profile, school):
    try:
        alum = Alum.objects.get(user=profile, school=school)
        return alum.year
    except Alum.DoesNotExist:
        return None
