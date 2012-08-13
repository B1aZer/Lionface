from django import template
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from account.models import *

register = template.Library()

# Filter to check if a user is friends with another user
@register.filter(name='has_friend')
def has_friend(user, friend):
    return user.has_friend(friend)

@register.filter(name='has_friend_request')
def has_friend_request(user, friend):
    return user.has_friend_request(friend)

@register.filter(name='show_friend_count')
def show_friend_count(user):
    wordarray = ['Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    count = "Nobody is"
    num = user.friends.all().count()
    if(num == 1): count = "One person is"
    elif( num > 0 and num < 10): count = "%s people are" % (wordarray[num-2])
    elif( num > 0): count = "%d people are" % (num)
    return "%s following you publicly." % (count)
