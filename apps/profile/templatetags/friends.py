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

@register.filter(name='in_hidden')
def in_hidden(user, friend):
    return user.in_hidden(friend)

@register.filter(name='in_followers')
def in_followers(user, friend):
    return user.in_followers(friend)

@register.filter(name='show_friend_count')
def show_friend_count(user, current=None):
    wordarray = ['2', '3', '4', '5', '6', '7', '8', '9']
    count = "0 Friends"
    if not current:
        num = user.get_friends_count()
    else:
        num = user.get_friends_count(current)
    if(num == 1): count = "%s Friend" % (num)
    elif( num > 0 and num < 10): count = "%s Friends" % (wordarray[num-2])
    elif( num > 0): count = "%d Friends" % (num)
    return "%s" % (count)

@register.filter(name='show_following_count')
def show_following_count(user, current=None):
    if current:
        return user.get_following_count(current)
    else:
        return user.get_following_count()

@register.filter(name='show_followers_count')
def show_followers_count(user, current=None):
    if current:
        return user.get_followers_count(current)
    else:
        return user.get_followers_count()

@register.filter(name='check_following')
def check_following(profile, user):
    show = False
    if profile.check_option('follow',"Public"):
        show = True
    elif profile.check_option('follow',"Friend's Friends"):
        if profile.has_friends_friend(user):
            show = True
    elif profile.check_option('follow',"Off"):
        show = False
    else:
        show = True
    return show

@register.filter(name='mutual_friends')
def mutual_friends(current, user):
    return current.get_mutual_friends(user)

@register.filter(name='list_mutual_friends')
def list_mutual_friends(current, user):
    return current.list_mutual_friends(user)

@register.filter(name='degree_of_separation')
def degree_of_separation(current, user):
    return current.get_degree_for(user)






