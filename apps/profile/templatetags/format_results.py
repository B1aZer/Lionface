from django import template
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.models import User
from tags.models import *
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
                    result.append(news_item[0])
        return render_to_string('post/_feed.html', { 'items': result },RequestContext(request))
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

