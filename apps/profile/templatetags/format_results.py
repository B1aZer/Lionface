from django import template
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.models import User
from django.utils.html import escape
from django.utils.safestring import mark_safe
from tags.models import *
from pages.models import Pages
from smileys.models import Smiley
import re
from pages.forms import BUSINESS_CATEGORY, NONPROFIT_CATEGORY

register = template.Library()


# Function to format a search result.
@register.filter(name='format_result')
def format_result(object, current_user):
    if isinstance(object, User):
        return render_to_string('search/_result_user.html', { 'user': object, 'current_user': current_user })
    if isinstance(object, Pages):
        return render_to_string('search/_result_page.html', { 'page': object, 'current_user': current_user })
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
                else:
                    result.append(item)

        if result:
            result = sorted(result,key=lambda post: post.date, reverse=True)
        return render_to_string('search/_feed.html', { 'items': result },RequestContext(request))
    return ""


# Function to format a search result.
@register.filter(name='format_image')
def format_image(photo, path=""):
    #import pdb;pdb.set_trace()
    photo_name = getattr(photo, "name", None)
    if photo_name:
        photo = photo_name
    else:
        photo = photo
    if 'noProfilePhoto.png' in photo:
        photo = 'uploads/images/noProfilePhoto.png'
    """
    if '/lionface/' in path:
        photo = "lionface/%s" % photo
    """
    return photo


@register.filter(name='format_thumb')
def format_thumb(image, path=''):
    if hasattr(image, 'thumb_name'):
        image = getattr(image, 'thumb_name')
    if 'noProfilePhoto.thumb.png' in image:
        image = 'uploads/images/noProfilePhoto.thumb.png'
    if '/lionface/' in path:
        image = "lionface/%s" % image
    return image


# Function for stripping tags.
@register.filter(name='strip_comment')
def strip_comment(comment):
    import bleach
    comment = bleach.clean(comment,attributes={'a': ['href', 'rel', 'name'],})
    comment = bleach.linkify(comment,target='_top',title=True)
    return comment


@register.filter(name='get_comment_counter')
def get_comment_counter(item, user):
    try:
        counter = item.get_comment_counter(user)
    except:
        counter = 0
    return counter


# Function for stripping tags.
@register.filter(name='color_tags',is_safe=True)
def color_tags(text):
    # Has problems with urls(#) (?<!http)
    text = re.sub(r'((?:\A|\s)#([\w]+))',r'<a href="/tag/?models=tags_tag&q=\2" class="colored_tag">\1</a>',text)
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
        try:
            img = '<img class="smiley" src="/%s" alt="%s" height="%i" width="%i" />' % (smiley.image.url, smiley.description, smiley.image.height, smiley.image.width)
        except:
            # someone deleted file from smileys directory
            img = smiley.pattern
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

@register.filter(name='check_profile_image_visibility')
def check_profile_image_visibility(user, current_user):
    print user.check_visiblity('profile_image', current_user)
    return user.check_visiblity('profile_image', current_user)

@register.filter(name='check_message_sending')
def check_message_sending(user,current):
    return user.check_visiblity('send_message',current)

@register.filter(name='check_friend_request')
def check_friend_request(user,current):
    return user.check_visiblity('add_friend',current)


@register.filter(name='escaping')
def escaping(value):
    return escape(value)

@register.filter(name='follows')
def follows(item,user):
    if item.get_type() in ['content post','share post','page post','feedback post'] and not user.is_anonymous() :
        return item.get_post() in user.follows.all()
    return False

@register.filter(name='following')
def following(item):
    return item.get_post().following.count()

@register.filter(is_safe=True, needs_autoescape=True)
def excerpt(value, autoescape=None):
    lines = value.split(u'\n')
    # Find the maximum width of the line count, for use with zero padding
    # string format command
    length = len(lines)
    if length > 7:
        lines.insert(7,'<a href="#" class="excerpt">Show Entire Post</a>')
    #for i, line in enumerate(lines):
            #lines[i] = (u"%0" + width  + u"d. %s") % (i + 1, line)
    return mark_safe(u'\n'.join(lines))

@register.filter(name="mark_read")
def mark_read(message):
    message.mark_read()
    return ""

# Permission filters for pages
@register.filter(name="check_pages_basics")
def check_pages_basics(user,page):
    if user.is_anonymous():
        return False
    return user.check_option('pages_basics__%s' % page.id)

@register.filter(name="check_pages_delete")
def check_pages_delete(user,page):
    if user.is_anonymous():
        return False
    return user.check_option('pages_delete__%s' % page.id)

@register.filter(name="check_pages_admins")
def check_pages_admins(user,page):
    if user.is_anonymous():
        return False
    return user.check_option('pages_admins__%s' % page.id)

@register.filter(name="check_pages_photos")
def check_pages_photos(user,page):
    if user.is_anonymous():
        return False
    return user.check_option('pages_photos__%s' % page.id)

@register.filter(name="check_pages_updates")
def check_pages_updates(user,page):
    if user.is_anonymous():
        return False
    return user.check_option('pages_updates__%s' % page.id)

@register.filter(name="check_pages_calendar")
def check_pages_calendar(user,page):
    if user.is_anonymous():
        return False
    return user.check_option('pages_calendar__%s' % page.id)

@register.filter(name="check_pages_loves")
def check_pages_loves(user,page):
    if user.is_anonymous():
        return False
    return user.check_option('pages_loves__%s' % page.id)

@register.filter(name="check_pages_community")
def check_pages_community(user,page=None):
    if user.is_anonymous():
        return False
    if not page:
        return user.get_community_pages_count()
    return user.check_option('pages_community__%s' % page.id)

@register.filter(name="check_profile_eiv")
def check_profile_eiv(user,current):
    return user.check_visiblity('vie_profile',current)

@register.filter(name="check_pages_eiv_private")
def check_pages_eiv_private(user,current):
    if user == current:
        return False
    else:
        return user.check_option('vie_pages','Private')

@register.simple_tag(takes_context=True)
def check_three_arguments(context, *args, **kwargs):
    """
    Tag with >2 arguments
    {% check_three_arguments profile_user page request.user as 'member_filter' %}
    """
    if len(args) > 3:
        as_name = 'filter_value'
        user = args[0]
        page = args[1]
        current = args[2]
        name = "pages__%s" % page
        if len(args) == 5:
            as_name = args[-1]
        context[as_name] = user.check_visiblity(name,current)
    return ''


@register.filter(name="get_community_pages_friends")
def get_community_pages_friends(user,page):
    return user.get_community_pages_friends(page)

@register.filter(name="get_community_friends_for")
def get_community_friends_for(user,page):
    return user.get_community_pages_count(page)


@register.filter(name="show_membership")
def show_membership(page,user):
    if user.is_anonymous():
        return []
    return page.show_membership(user)

@register.filter(name="show_connections")
def show_connections(page,user):
    if user.is_anonymous():
        return []
    return page.show_connections(user)


@register.filter(name="sort_dict")
def sort_dict(dcty):
    dcty = sorted(dcty.iteritems(), key=lambda (k,v): k)
    return dcty


@register.filter(name="getcatnumnonp")
def getcatnumnonp(cat):
    tup = (cat,cat)
    val = NONPROFIT_CATEGORY.index(tup)
    return val

@register.filter(name="getcatnumbusn")
def getcatnumbusn(cat):
    tup = (cat,cat)
    val = BUSINESS_CATEGORY.index(tup)
    return val


@register.filter(name="posted_review_for")
def posted_review_for(user, page):
    return user.posted_review_for(page)


@register.filter(name="get_current_bid_for")
def get_current_bid_for(user, page):
    bid = user.get_current_bid_for(page)
    if bid:
        bid = bid.amount
    else:
        bid = 0
    return bid


@register.filter(name="is_customer_for")
def is_customer_for(user, page):
    return user.is_customer_for(page)

@register.filter(name="is_lcustomer_for")
def is_lcustomer_for(user, page):
    return user.is_lcustomer_for(page)

@register.filter(name="get_love_last_4")
def get_love_last_4(user,page):
    return user.get_love_last_4(page)

@register.filter(name="get_last_four")
def get_last_four(user,page):
    return user.get_last_4(page)

@register.filter(name="get_love_card_type_for")
def get_love_card_type_for(user,page):
    return user.get_love_card_type_for(page)

@register.filter(name="get_card_type")
def get_card_type(user,page):
    return user.get_card_type_for(page)

@register.filter(name="format_date")
def format_date(dt):
    dt = int(dt) / 100
    if dt > 0:
        dt = "+%s" % dt
    if dt == 0:
        dt = ''
    return dt
