from django import template
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.models import User
from django.utils.html import escape
from tags.models import *
from smileys.models import Smiley
import re

register = template.Library()

# Function to format a search result.
@register.filter(name='format_result')
def format_result(object, current_user):
    if isinstance(object, User):
        return render_to_string('search/_result_user.html', { 'user': object, 'current_user': current_user })
    return ""

@register.filter(name='format_tag')
def format_tag(object,request):
    if isinstance(object, Tag):
        items = object.post_set.all()
        result = []
        if items:
            for item in items:
                news_item = item.newsitem_set.all()
                if news_item:
                    if request.user.has_friend(item.user) or request.user == item.user or news_item[0].get_privacy == 'P':
                        result.append(news_item[0])
        if result:
            result = sorted(result,key=lambda post: post.date, reverse=True)
        return render_to_string('search/_feed.html', { 'items': result },RequestContext(request))
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
    if '/lionface/' in path:
        photo = "lionface/%s" % photo
    return photo

# Function for stripping tags.
@register.filter(name='strip_comment')
def strip_comment(comment):
    import bleach
    comment = bleach.clean(comment,attributes={'a': ['href', 'rel', 'name'],})
    comment = bleach.linkify(comment,target='_top',title=True)
    return comment

# Function for stripping tags.
@register.filter(name='color_tags',is_safe=True)
def color_tags(text):
    text = re.sub(r'(#([\w]+))',r'<a href="/tag/?models=tags_tag&q=\2" style="color: #A70; text-decoration: underline;">\1</a>',text)
    return text

@register.filter(name='smileys',is_safe=True)
def smileys(value):
    """
    Replaces all occurrences of the active smiley patterns in `value` with a
    tag that points to the image associated with the respective pattern.

    """
    value = value.replace("&lt;3","<3")

    for smiley in Smiley.objects.all():
        # come up with the <img> tag
        img = '<img class="smiley" src="/%s" alt="%s" height="%i" width="%i" />' % (smiley.image.url, smiley.description, smiley.image.height, smiley.image.width)
        if False:
            # regex patterns allow you to use the same Smiley for multiple
            # ways to type a smiley
            value = re.sub(smiley.pattern, img, value)
        else:
            # this is the stupid (strict) way
            value = value.replace(smiley.pattern, img)

    #value = value.replace("<", "&lt;").replace(">","&gt;")

    return value

@register.filter(name='check_option')
def check_option(user,name):
    return user.check_option(name)

@register.filter(name='check_friends_visibility')
def check_friends_visibility(user,current):
    return user.check_visiblity('friend_list',current)

@register.filter(name='check_follower_visibility')
def check_follower_visibility(user,current):
    return user.check_visiblity('follower_list',current)

@register.filter(name='check_following_visibility')
def check_following_visibility(user,current):
    return user.check_visiblity('following_list',current)

@register.filter(name='check_message_sending')
def check_message_sending(user,current):
    return user.check_visiblity('send_message',current)

@register.filter(name='escaping')
def escaping(value):
    return escape(value)



