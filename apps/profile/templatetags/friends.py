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

@register.filter(name='in_followers')
def in_followers(user, friend):
    return user.in_followers(friend)


@register.filter(name='show_friend_count')
def show_friend_count(user):
    wordarray = ['2', '3', '4', '5', '6', '7', '8', '9']
    count = "0 Friends"
    num = user.friends.all().count()
    if(num == 1): count = "%s Friend" % (num)
    elif( num > 0 and num < 10): count = "%s Friends" % (wordarray[num-2])
    elif( num > 0): count = "%d Friends" % (num)
    return "%s" % (count)
