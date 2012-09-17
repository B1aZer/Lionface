from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from .forms import MessageForm
from .models import Messages
from account.models import UserProfile
from django.db.models import Count, Max
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

try:
    import json
except ImportError:
    import simplejson as json

@login_required
def messages(request):
    form = MessageForm()
    send = False

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            user_to_id = form.cleaned_data['user_id']
            user_to = UserProfile.objects.get(id=int(user_to_id))
            content = form.cleaned_data['content']
            mess = Messages(user=request.user,user_to=user_to,content=content)
            send = mess.save()
            form = MessageForm()

    messages_in = Messages.objects.filter(user_to=request.user).order_by('date')
    messages_out = Messages.objects.filter(user=request.user).order_by('date')
    #adm = UserProfile.objects.filter(id=2).annotate(num_mess_to=Count('message_to'),last_date=Max('message_to__date'))
    #import pdb;pdb.set_trace()
    users = []
    names = []
    user = request.user
    for message in messages_in:
        if not message.user in users:
            users.append(message.user)
            mess_sent = Messages.objects.filter(user_to=message.user, user = user).count()
            mess_recv = Messages.objects.filter(user=message.user, user_to = user).count()
            mess_new  = Messages.objects.filter(user=message.user, user_to = user, read=False).count()
            mess_all = int(mess_sent) + int(mess_recv)
            link = message.user.get_absolute_url()
            image = message.user.photo
            id_user = message.user.id
            last_mess = Messages.objects.filter(Q(user_to=message.user, user = user) | Q(user=message.user, user_to = user)).latest('date').date
            names.append({ 'name':message.user.full_name,'mess_all':mess_all,'mess_sent':mess_sent,'mess_recv':mess_recv, 'mess_new':mess_new,
                'link':link, 'image':image, 'id': id_user, 'last_mess' : last_mess})
    for message in messages_out:
        if not message.user_to in users:
            users.append(message.user_to)
            mess_sent = Messages.objects.filter(user_to=message.user_to, user = user).count()
            mess_recv = Messages.objects.filter(user=message.user_to, user_to = user).count()
            mess_new  = Messages.objects.filter(user=message.user_to, user_to = user, read=False).count()
            mess_all = int(mess_sent) + int(mess_recv)
            link = message.user_to.get_absolute_url()
            image = message.user_to.photo
            id_user = message.user_to.id
            last_mess = Messages.objects.filter(Q(user_to=message.user_to, user = user) | Q(user=message.user_to, user_to = user)).latest('date').date
            names.append({ 'name':message.user_to.full_name,'mess_all':mess_all,'mess_sent':mess_sent,'mess_recv':mess_recv, 'mess_new':mess_new, 'link':link, 'image':image, 'id': id_user, 'last_mess' : last_mess})

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
                    'messages':names,
                }, context_instance=RequestContext(request))
            return HttpResponse(json.dumps(data), "application/json")

    return render_to_response(
        'messages/messages.html',
        {
            'form':form,
            'send':send,
            'messages':names,
        },
        RequestContext(request)
    )

@login_required
def show(request):
    data = {'status': 'OK'}
    if request.method == 'POST' and 'user_id' in request.POST:
        user = UserProfile.objects.get(id=int(request.POST['user_id']))

        messages = Messages.objects.filter(Q(user_to=request.user, user = user) | Q(user=request.user, user_to = user)).order_by('date')
        messages_to = Messages.objects.filter(user_to=request.user).order_by('date')
        for mess in messages_to:
            mess.mark_read()

        if 'sort' in request.POST:
            sort = request.POST['sort']
            if sort == 'desc':
                messages = messages.order_by('-date')
                request.user.set_option('reverse','desc')
            elif sort == 'asc':
                messages = messages.order_by('date')
                request.user.set_option('reverse','asc')
            else:
                if request.user.check_option('reverse','asc'):
                    messages = messages.order_by('date')
                elif request.user.check_option('reverse','desc'):
                    messages = messages.order_by('-date')



        data['html'] = render_to_string('messages/feed.html',
                {
                    'messages':messages,
                }, context_instance=RequestContext(request))
        data['sort'] = request.user.check_option('reverse') or 'asc'

    return HttpResponse(json.dumps(data), "application/json")
