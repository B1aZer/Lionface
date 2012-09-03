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
    photo_name = getattr(photo, "name", None)
    if photo_name:
        photo = photo_name
    else:
        photo = photo
    if 'noProfilePhoto.png' in photo:
        photo = 'uploads/images/noProfilePhoto.png'
    if 'lionface' in path:
        photo = "lionface/%s" % photo
    return photo

# Function for identifying frinds.
@register.filter(name='find_friend')
def find_friend(user, friend):
    #import pdb;pdb.set_trace()
    if user == friend or user.has_friend(friend):
        return True
    else:
        return False

