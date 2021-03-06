from django.http import *
from django.contrib.auth.decorators import login_required
from account.decorators import active_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from .forms import MessageForm
from .models import Messaging
from account.models import UserProfile
from django.db.models import Count, Max
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
import pytz

try:
    import json
except ImportError:
    import simplejson as json

@active_required
@login_required
def messages(request, username=None):
    form = MessageForm()
    send = False
    user_id_after = ''

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            user_to_id = form.cleaned_data.get('user_id')
            if not user_to_id:
                try:
                    user_to = UserProfile.objects.get(username = form.cleaned_data.get('user_to'))
                    content = form.cleaned_data['content']
                    mess = Messaging(user=request.user,user_to=user_to,content=content)
                    send = mess.save()
                    if send:
                        user_id_after = user_to.id
                    form = MessageForm()
                except:
                    form = MessageForm()
            else:
                user_to = UserProfile.objects.get(id=int(user_to_id))
                content = form.cleaned_data['content']
                mess = Messaging(user=request.user,user_to=user_to,content=content)
                send = mess.save()
                form = MessageForm()

    messages_in = Messaging.objects.filter(user_to=request.user).order_by('date')
    messages_out = Messaging.objects.filter(user=request.user).order_by('date')
    #adm = UserProfile.objects.filter(id=2).annotate(num_mess_to=Count('message_to'),last_date=Max('message_to__date'))
    #import pdb;pdb.set_trace()
    users = []
    names = []
    user = request.user
    for message in messages_in:
        if not message.user in users:
            flag = 'today'
            users.append(message.user)
            mess_sent = Messaging.objects.filter(user_to=message.user, user = user).count()
            mess_recv = Messaging.objects.filter(user=message.user, user_to = user).count()
            mess_new  = Messaging.objects.filter(user=message.user, user_to = user, read=False).count()
            mess_all = int(mess_sent) + int(mess_recv)
            link = message.user.get_absolute_url()
            image = message.user.photo
            id_user = message.user.id
            last_obj = Messaging.objects.filter(Q(user_to=message.user, user = user) | Q(user=message.user, user_to = user)).latest('date')
            last_mess = last_obj.date
            now = timezone.now()
            diff_date = now - last_mess
            if diff_date.days <= 0:
                last_date = last_mess.strftime("%I:%M %p")
            elif diff_date.days >0 and last_mess.year == now.year:
                flag = 'week'
                last_date = last_mess.strftime("%b %d")
            else:
                flag = 'year'
                last_date = last_mess.strftime("%b %Y")
            names.append({ 'name':message.user.full_name, 'thumb':message.user.get_thumb(), 'mess_all':mess_all,'mess_sent':mess_sent,'mess_recv':mess_recv, 'mess_new':mess_new,
                'link':link, 'image':image, 'id': id_user, 'last_obj':last_obj, 'last_date':last_date, 'last_date_type': flag, 'last_mess' : last_mess})
        # This counter is for main page only
        message.mark_viewed()

    for message in messages_out:
        if not message.user_to in users:
            users.append(message.user_to)
            mess_sent = Messaging.objects.filter(user_to=message.user_to, user = user).count()
            mess_recv = Messaging.objects.filter(user=message.user_to, user_to = user).count()
            mess_new  = Messaging.objects.filter(user=message.user_to, user_to = user, read=False).count()
            mess_all = int(mess_sent) + int(mess_recv)
            link = message.user_to.get_absolute_url()
            image = message.user_to.photo
            id_user = message.user_to.id
            last_obj = Messaging.objects.filter(Q(user_to=message.user_to, user = user) | Q(user=message.user_to, user_to = user)).latest('date')
            last_mess = last_obj.date
            now = timezone.now()
            diff_date = now - last_mess
            if diff_date.days <= 0:
                flag = 'today'
                last_date = last_mess.strftime("%I:%M %p %z")
            elif diff_date.days >0 and last_mess.year == now.year:
                flag = 'week'
                last_date = last_mess.strftime("%b %d")
            else:
                flag = 'year'
                last_date = last_mess.strftime("%b %Y")
            names.append({ 'name':message.user_to.full_name, 'thumb':message.user.get_thumb(), 'mess_all':mess_all,'mess_sent':mess_sent,'mess_recv':mess_recv, 'mess_new':mess_new, 'link':link, 'image':image, 'id': id_user, 'last_obj':last_obj, 'last_date':last_date, 'last_date_type': flag, 'last_mess' : last_mess})

    #sorting by last message date
    names = sorted(names, key=lambda(s): s['last_mess'], reverse=True)

    paginator = Paginator(names, 7)
    names = paginator.page(1)

    if request.method == 'GET':
        page = request.GET.get('page',None)
        if page:
            try:
                names = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                names = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                names = paginator.page(paginator.num_pages)

            data = render_to_string('messages/users.html',
                {
                    'user_messages':names,
                }, context_instance=RequestContext(request))
            return HttpResponse(json.dumps(data), "application/json")

    return render_to_response(
        'messages/messages.html',
        {
            'form':form,
            'send':send,
            'user_messages':names,
            'user_id_after':user_id_after,
        },
        RequestContext(request)
    )

@active_required
@login_required
def show(request, username=None):
    data = {'status': 'OK'}
    max_mess = 7
    if request.method == 'POST' and 'user_id' in request.POST:
        user = UserProfile.objects.get(id=int(request.POST['user_id']))

        messages = Messaging.objects.filter(Q(user_to=request.user, user = user) | Q(user=request.user, user_to = user)).order_by('-date')

        #import pdb;pdb.set_trace()
        page = int(request.POST.get('page', 1))
        all_mess = messages.count()

        if page == 1:
            messages = messages[:max_mess]
            last_mess = max_mess
        else:
            offset = (page - 1) * max_mess
            last_mess = offset + max_mess
            messages = messages[offset:last_mess]

        if all_mess - last_mess > 0:
            next_page = page + 1
        else:
            next_page = page


        if 'sort' in request.POST:
            sort = request.POST['sort']
            if sort == 'desc':
                #messages = messages.order_by('-date')
                request.user.set_option('reverse','desc')
            elif sort == 'asc':
                messages = list(reversed(messages))
                #messages = messages.order_by('date')
                request.user.set_option('reverse','asc')
            else:
                if request.user.check_option('reverse','asc'):
                    #messages = messages.order_by('date')
                    messages = list(reversed(messages))
                elif request.user.check_option('reverse','desc'):
                    #messages = messages.order_by('-date')
                    pass

        data['html'] = render_to_string('messages/feed.html',
                {
                    'user_messages':messages,
                }, context_instance=RequestContext(request))
        data['sort'] = request.user.check_option('reverse') or 'asc'
        data['page'] = page
        data['nextpage'] = next_page
        data['mr'] = Messaging.objects.filter(user_to=request.user, user = user).count()
        data['ms'] = Messaging.objects.filter(user=request.user, user_to = user).count()

        # Marking read for all
        messages_to = Messaging.objects.filter(user_to=request.user).order_by('date')
        for mess in messages_to:
            mess.mark_read()

    return HttpResponse(json.dumps(data), "application/json")
