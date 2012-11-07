from django.http import *
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from .forms import *
from .models import *
from post.models import PagePost
from tags.models import Tag
from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from StringIO import StringIO
import base64

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

    form = ImageUploadForm()
    data_uri = ''
    restrict_height = 300
    target_width = 900
    resize = False

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

    image_height = page.cover_photo.height

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['cover_photo']
            # save to memory
            f = StringIO(image.read())
            # PIL image
            img = Image.open(f)
            ( width, height) = img.size
            if width < target_width:
                target_height = int(height * (1.0 * target_width / width))
                img = img.resize( (target_width, target_height) )
            elif width > target_width:
                target_height = int(height * (1.0 * target_width / width))
                img.thumbnail((target_width,target_height), Image.ANTIALIAS)
            else:
                pass
            ( new_width, new_height) = img.size
            if new_height != restrict_height:
                resize= True
            # save to memory
            thumb = StringIO()
            img.save(thumb, 'JPEG')
            thumb.seek(0)
            thumb_file = InMemoryUploadedFile(thumb, None, image.name, image.content_type, thumb.len, image.charset)

            # we can save it
            #if page.cover_photo and page.cover_photo.name != page.cover_photo.field.default:
                #page.cover_photo.delete()
            #page.cover_photo = thumb_file
            #page.save()
            # or we can return it to template

            class DataURI:
                def __init__(self):
                    self.width = 0
                    self.height = 0
                    self.data_uri = None
                def __repr__(self):
                    return self.data_uri

            data_uri = DataURI()
            data_uri.data_uri = 'data:image/jpg;base64,'
            data_uri.data_uri += thumb.getvalue().encode('base64').replace('\n', '')
            data_uri.width = new_width
            data_uri.height = new_height

            image_height = data_uri.height

    if page.type == 'BS':
        template = 'pages/page.html'
    else:
        template = 'pages/page_nonprofit.html'

    cover_offset = (image_height - restrict_height - 95) * -1
    if resize:
        return render_to_response(
            "pages/page_cover.html",
            {
                'page': page,
                'form': form,
                'cover_offset': cover_offset,
                'data_uri': data_uri,
            },
            RequestContext(request)
        )
    else:
        return render_to_response(
            template,
            {
                'page': page,
                'form': form,
                'image': data_uri,
            },
            RequestContext(request)
        )


def reposition(request, slug=None):
    data={'status':'FAIL'}
    if not slug:
        raise Http404

    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404

    if request.method == 'POST' and 'top' in request.POST:
        top_pos = abs(int(request.POST['top']))
        b64image = request.POST.get('image',None)
        #decoded_image = base64.b64decode(b64image + '=' * (-len(b64image) % 4))
        imgstr = re.search(r'base64,(.*)', b64image).group(1)
        mem_image = StringIO(imgstr.decode('base64'))
        #image = page.cover_photo
        img = Image.open(mem_image)
        box = (0, top_pos, 900, top_pos+300)
        img = img.crop(box)

        cropped = StringIO()
        img.save(cropped, 'JPEG')
        cropped.seek(0)
        image_name = "%s_cover_image.jpg" % page.username
        cropped_file = InMemoryUploadedFile(cropped, None, image_name, 'image/jpeg', cropped.len, None)
        #cropped_file = InMemoryUploadedFile(cropped, image.field, image.name, 'image/jpeg', cropped.len, None)
        if page.cover_photo.name != page.cover_photo.field.default:
            page.cover_photo.delete()
        page.cover_photo = cropped_file
        page.save()
    return HttpResponse(json.dumps(data), "application/json")


def reset_picture(request, slug=None):
    if not slug:
        raise Http404

    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404

    if page.user == request.user:
        if page.cover_photo.name != page.cover_photo.field.default:
            page.cover_photo.delete()
        page.cover_photo = page.cover_photo.field.default
        page.save()
    if page.type == 'BS':
        redrct = redirect('business-page', slug=page.username)
    else:
        redrct = redirect('nonprofit-page', slug=page.username)
    return redrct


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
                post = PagePost(user=request.user, content=content, page = page)
                post.save()

                #Tags
                hashtags = [word[1:] for word in content.split() if word.startswith('#')]

                for hashtag in hashtags:
                    try:
                        tag = Tag.objects.get(name__iexact=hashtag)
                        post.tags.add(tag)
                    except ObjectDoesNotExist:
                        post.tags.create(name=hashtag)
                    except MultipleObjectsReturned:
                        tags = Tag.objects.filter(name__iexact=hashtag)
                        tag = [p for p in tags if not hasattr(p, 'user_tag')]
                        if tag:
                            post.tags.add(tag[0])

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
