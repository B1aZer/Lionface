from django.http import *
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from .forms import *
from .models import *
from itertools import chain

try:
    import json
except ImportError:
    import simplejson as json

def main(request, username=None):

    form = PageForm()
    active = None

    if request.method == 'POST':
        form = PageForm(data = request.POST)
        if request.POST.get('type',None) == 'NP':
            active = 'Nonprofit'
        else:
            active = "Business"
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            # nullify form
            active = None
            form = PageForm()

    pages = Pages.objects.filter(type='BS')

    # grouping by rows for template [4 in row]
    n=0
    grouped_pages = []
    row = []
    for page in pages:
        n += 1
        row.append(page)
        if n%4 == 0 or n == pages.count():
            grouped_pages.append(row)
            row = []

    pages = grouped_pages

    return render_to_response(
        'pages/business.html',
        {
            'form': form,
            'pages': pages,
            'active': active,
        },
        RequestContext(request)
    )

def page(request, slug=None, username=None):

    if not slug:
        raise Http404

    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404

    return render_to_response(
        'pages/page.html',
        {
            'page': page,
        },
        RequestContext(request)
    )

def leaderboard(request, username=None):

    return render_to_response(
        'pages/leaderboard.html',
        {
        },
        RequestContext(request)
    )

def nonprofit(request, username=None):

    pages = Pages.objects.filter(type='NP')

    # grouping by rows for template [4 in row]
    n=0
    grouped_pages = []
    row = []
    for page in pages:
        n += 1
        row.append(page)
        if n%4 == 0 or n == pages.count():
            grouped_pages.append(row)
            row = []

    pages = grouped_pages  

    return render_to_response(
        'pages/nonprofit.html',
        {
            'pages':pages,
        },
        RequestContext(request)
    )

def love_count(request):
    data = {'status':'FAIL'}
    if request.method == 'POST':
        page_id = request.POST.get('page_id')
        vote = request.POST.get('vote')
        if page_id:
            try:
                page = Pages.objects.get(id=int(page_id))
                if vote == 'up':
                    page.loves += 1
                    page.users_loved.add(request.user)
                    page.save()
                    data['status'] = 'OK'
                if vote == 'down':
                    page.loves -= 1
                    page.users_loved.remove(request.user)
                    page.save()
                    data['status'] = 'OK'
            except Pages.DoesNotExist:
                pass
    return HttpResponse(json.dumps(data), "application/json")
