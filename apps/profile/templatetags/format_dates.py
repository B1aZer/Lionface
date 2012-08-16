from django import template

register = template.Library()

# Function to format a search result.
@register.filter
def format_date(temp,tz):
    print temp
    print tz
    return tz




