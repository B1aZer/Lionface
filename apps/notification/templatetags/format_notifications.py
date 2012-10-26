from django import template
from django.template.loader import render_to_string
from notification.models import *

register = template.Library()

# Function to format a search result.
@register.filter(name='format_notification')
def format_notification(notification):
    if not notification.read:
        notification.new_one = True
    data = { 'notification': notification }
    notification.mark_read()
    if notification.type == 'FR':
        return render_to_string('notification/_friend_request.html', data)
    if notification.type == 'FA':
        return render_to_string('notification/_friend_accept.html', data)
    if notification.type == 'CS':
        return render_to_string('notification/_comment_submitted.html', data)
    if notification.type == 'PS':
        return render_to_string('notification/_shared_post.html', data)
    if notification.type == 'PP':
        return render_to_string('notification/_profile_post.html', data)
    if notification.type == 'FF':
        return render_to_string('notification/_follow_user.html', data)
    if notification.type == 'FC':
        return render_to_string('notification/_follow_comment.html', data)
    if notification.type == 'FS':
        return render_to_string('notification/_follow_shared.html', data)
    if notification.type == 'MC':
        return render_to_string('notification/_comment_multiple.html', data)
    if notification.type == 'MF':
        return render_to_string('notification/_follow_comment_multiple.html', data)
    if notification.type == 'MS':
        return render_to_string('notification/_shared_post_multiple.html', data)
    if notification.type == 'MM':
        return render_to_string('notification/_follow_shared_multiple.html', data)
    if notification.type == 'FM':
        return render_to_string('notification/_follow_user_multiple.html', data)
    if notification.type == 'MP':
        return render_to_string('notification/_profile_post_multiple.html', data)
    return ""

