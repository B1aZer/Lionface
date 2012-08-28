from django import template
from django.template.loader import render_to_string
from django.contrib.auth.models import User

register = template.Library()

# Function to format a search result.
@register.filter(name='format_result')
def format_result(object, current_user):
    if isinstance(object, User):
        return render_to_string('search/_result_user.html', { 'user': object, 'current_user': current_user })
    return ""

# Function to format a search result.
@register.filter(name='format_image')
def format_image(photo, path):
    #import pdb;pdb.set_trace()
    if 'noProfilePhoto.png' in photo.name:
        photo = 'uploads/images/noProfilePhoto.png'
    if 'lionface' in path:
        photo = "lionface/%s" % photo.name
    return photo

