from django.http import *
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from .forms import *
from .models import *
from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

try:
    import json
except ImportError:
    import simplejson as json

def main(request):

    form_busn = BusinessForm()
    form_nonp = NonprofitForm()
    active = None

    if request.method == 'POST' and request.POST.get('type',None):
        if request.POST.get('type',None) == 'NP':
            active = 'Nonprofit'
            form = NonprofitForm(data = request.POST)
            form_nonp = form
        else:
            active = "Business"
            form = BusinessForm(data = request.POST)
            form_busn = form
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            # nullify form
            active = None
            form = PageForm()
            form_busn = BusinessForm()
            form_nonp = NonprofitForm()

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
            'form_busn': form_busn,
            'form_nonp': form_nonp,
            'pages': pages,
            'active': active,
        },
        RequestContext(request)
    )

def page(request, slug=None):

    if not slug:
        raise Http404

    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404

    if request.method == 'GET' and 'ajax' in request.GET:
        data = {}
        template_name = request.GET.get('template_name',None)
        if template_name:
            try:
                data['html'] = render_to_string('pages/micro/%s.html' % template_name,
                {
                    'page': page,
                }, context_instance=RequestContext(request))
            except TemplateDoesNotExist:
                data['html'] = "Sorry! Wrong template."
            return HttpResponse(json.dumps(data), "application/json")

    if page.type == 'BS':
        template = 'pages/page.html'
    else:
        template = 'pages/page_nonprofit.html'

    return render_to_response(
        template,
        {
            'page': page,
        },
        RequestContext(request)
    )

def leaderboard(request):

    return render_to_response(
        'pages/leaderboard.html',
        {
        },
        RequestContext(request)
    )

def nonprofit(request):

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

@login_required
def update(request):
    data = {'status':'FAIL'}
    if request.method == 'POST' and 'page_id' in request.POST:
        page_id = request.POST.get('page_id')
        content = request.POST.get('content')
        try:
            page = Pages.objects.get(id=int(page_id))
            if page.user == request.user:
                page.posts.create(user=request.user, content=content)
                data['status'] = 'OK'
        except Pages.DoesNotExist:
            pass
    return HttpResponse(json.dumps(data), "application/json")

def list_posts(request, slug=None):
    data = {'status':'FAIL'}
    if not slug:
        HttpResponse(json.dumps(data), "application/json")
    if slug:
        try:
            page_obj = Pages.objects.get(username=slug)
            items = page_obj.get_posts().order_by('-date')
        except Pages.DoesNotExist:
            raise Http404

    # PAGINATION #
    paginator = Paginator(items, 7)
    items = paginator.page(1)

    if request.method == 'GET':
        page = request.GET.get('page', None)
        if page:
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                items = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                items = paginator.page(paginator.num_pages)
        else:
            page = 1

    data['html'] = render_to_string('post/_page_feed.html',
            {
                'items':items,
                'page':page,
            }, context_instance=RequestContext(request))
    data['status'] = 'OK'
    return HttpResponse(json.dumps(data), "application/json")
