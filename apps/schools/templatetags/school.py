import datetime
from django import template

from schools.models import Alum

register = template.Library()


@register.assignment_tag()
def school_years(alum_year):
    return range(alum_year - 6, alum_year) + range(alum_year, alum_year + 7)


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
