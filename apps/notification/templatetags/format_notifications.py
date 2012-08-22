from django import template
from django.template.loader import render_to_string
from notification.models import *

register = template.Library()

# Function to format a search result.
@register.filter(name='format_notification')
def format_notification(notification):
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
    return ""

