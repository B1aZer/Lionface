from django.http import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from .forms import MessageForm
from .models import Messages
from account.models import UserProfile
from django.db.models import Count, Max

@login_required
def messages(request):
    form = MessageForm()
    send = False
    messages = Messages.objects.filter(user_to=request.user).order_by('date')
    #adm = UserProfile.objects.filter(id=2).annotate(num_mess_to=Count('message_to'),last_date=Max('message_to__date'))
    #import pdb;pdb.set_trace()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            user_to_id = form.cleaned_data['user_id']
            user_to = UserProfile.objects.get(id=int(user_to_id))
            content = form.cleaned_data['content']
            mess = Messages(user=request.user,user_to=user_to,content=content)
            mess.save()
            send = True
    return render_to_response(
        'messages/messages.html',
        {
            'form':form,
            'send':send,
            'messages':messages,
        },
        RequestContext(request)
    )
