from django import template
from django.template.loader import render_to_string
from messaging.models import *
from account.models import UserProfile

register = template.Library()

# Function to format a search result.
@register.filter(name='format_list')
def format_list(messages,user):
    users = []
    names = []
    for message in messages:
        if not message.user in users:
            users.append(message.user)
            mess_sent = Messaging.objects.filter(user_to=message.user, user = user).count()
            mess_recv = Messaging.objects.filter(user=message.user, user_to = user).count()
            mess_new  = Messaging.objects.filter(user=message.user, user_to = user, read=False).count() 
            mess_all = int(mess_sent) + int(mess_recv)
            link = message.user.get_absolute_url()
            image = message.user.photo
            names.append({ 'name':message.user.full_name,'mess_all':mess_all,'mess_sent':mess_sent,'mess_recv':mess_recv, 'mess_new':mess_new,
                'link':link, 'image':image })
            #import pdb;pdb.set_trace()
    return names

