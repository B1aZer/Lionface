from django.http import *
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db.models import F
from .forms import *
from .models import *
from post.models import *
from tags.models import Tag
from agenda.models import Events, Locations
from ecomm.models import *
from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as pilImage
from StringIO import StringIO
import base64
import dateutil.parser
from datetime import datetime
import datetime as dateclass
from django.utils import timezone
from collections import defaultdict
import random
import cPickle

import stripe
import pytz

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

from images.models import Image, ImageComments
from images.forms import ImageForm


try:
    import json
except ImportError:
    import simplejson as json


def main(request):

    form_busn = BusinessForm()
    form_nonp = NonprofitForm()
    active = None
    max_pages = 12


    if request.method == 'POST' and request.user.get_pages().count() >= max_pages:
        messages.warning(request, 'Sorry only 12 pages are allowed')
    if request.method == 'POST' and request.POST.get('type', None) and request.user.get_pages().count() < max_pages:
        if request.POST.get('type', None) == 'NP':
            active = 'Nonprofit'
            form = NonprofitForm(data=request.POST)
            form_nonp = form
        else:
            active = "Business"
            form = BusinessForm(data=request.POST)
            form_busn = form
        if form.is_valid() and request.user.get_pages().count() < max_pages:
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            # nullify form
            active = None
            form = PageForm()
            form_busn = BusinessForm()
            form_nonp = NonprofitForm()

    pages = Pages.objects.filter(featured=False, type='BS').order_by('?')[:8]
    featured = Pages.objects.filter(featured=True, type='BS')
    if featured.count():
        fcount = featured.count()
        acount = 8 - fcount
        pages = list(chain(pages[:acount], featured))
        random.shuffle(pages)

    # grouping by rows for template [4 in row]
    n = 0
    grouped_pages = []
    row = []
    for page in pages:
        n += 1
        row.append(page)
        if n % 4 == 0 or n == len(pages):
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

    # micro templates
    if request.method == 'GET' and 'ajax' in request.GET:
        data = {}
        template_name = request.GET.get('template_name', None)
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

    if request.method == 'POST' \
        and 'album_image' in request.POST \
        and request.user.is_authenticated() \
            and request.user.check_option('pages_photos__%s' % page.id):
        album_form = ImageForm(request.POST, request.FILES)
        if album_form.is_valid():
            image = album_form.save(page)
            image.make_activity()
            image.generate_thumbnail(200, 200)
            # try:
            #     pil_object = pilImage.open(image.image.path)
            #     w, h = pil_object.size
            #     x, y = 0, 0
            #     if w > h:
            #         x, y, w, h = int((w-h)/2), 0, h, h
            #     elif h > w:
            #         x, y, w, h = 0, int((h-w)/2), w, w
            #     new_pil_object = pil_object \
            #         .crop((x, y, x+w, y+h)) \
            #         .resize((200, 200))
            #     new_pil_object.save(image.image.thumb_path)
            # except:
            #     pass
            name = 'business-page' if page.type == 'BS' else 'nonprofit-page'
            return redirect(name, slug=page.username)
    else:
        album_form = ImageForm()

    if request.method == 'POST' \
            and 'cover_image' in request.POST:
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['cover_photo']
            # save to memory
            f = StringIO(image.read())
            # PIL image
            img = pilImage.open(f)
            (width, height) = img.size
            if width < target_width:
                target_height = int(height * (1.0 * target_width / width))
                img = img.resize((target_width, target_height))
            elif width > target_width:
                target_height = int(height * (1.0 * target_width / width))
                img.thumbnail((target_width, target_height), pilImage.ANTIALIAS)
            else:
                pass
            (new_width, new_height) = img.size
            if new_height != restrict_height:
                resize = True
            # save to memory
            thumb = StringIO()
            img.save(thumb, 'JPEG')
            thumb.seek(0)
            thumb_file = InMemoryUploadedFile(thumb, None, image.name, image.content_type, thumb.len, image.charset)

            # we can save it
            #if page.cover_photo and page.cover_photo.name != page.cover_photo.field.default:
                #page.cover_photo.delete()
            if not resize:
                page.cover_photo = thumb_file
                page.save()
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

    if resize:
        cover_offset = (image_height - restrict_height - 95) * -1
        return render_to_response(
            "pages/page_cover.html",
            {
                'page': page,
                'form': form,
                'album_form': album_form,
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
                'album_form': album_form,
            },
            RequestContext(request)
        )


def reposition(request, slug=None):
    data = {'status': 'FAIL'}
    if not slug:
        raise Http404

    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404

    if request.method == 'POST' and 'top' in request.POST:
        top_pos = abs(int(request.POST['top']))
        b64image = request.POST.get('image', None)
        #decoded_image = base64.b64decode(b64image + '=' * (-len(b64image) % 4))
        imgstr = re.search(r'base64,(.*)', b64image).group(1)
        mem_image = StringIO(imgstr.decode('base64'))
        #image = page.cover_photo
        img = pilImage.open(mem_image)
        box = (0, top_pos, 900, top_pos + 300)
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


@login_required
def reset_album_activity(request, slug):
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404

    if request.user.check_option('pages_photos__%s' % page.id):
        if page.photo.name != page.photo.field.default:
            page.photo = page.photo.field.default
            page.save()
    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    name = 'business-page' if page.type == 'BS' else 'nonprofit-page'
    return redirect(name, slug=page.username)


def leaderboard(request):

    pages = Pages.objects.filter(type='BS').order_by('-loves')
    most_loved = pages[0]
    rest = pages[1:10]

    # group by cats
    c = 0
    row = defaultdict(list)
    gp = defaultdict(list)
    for page in pages:
        # grouping by rows for template [4 in row]
        row[page.category].append(page)
        c = len(row[page.category])
        if c % 3 == 0:
            gp[page.category].append(row[page.category])
            row[page.category] = []

    for k, v in row.items():
        if k not in gp:
            gp[k] = [v]
        else:
            if v not in gp[k]:
                gp[k].append(v)

    pages = gp

    return render_to_response(
        'pages/leaderboard.html',
        {
            'pages': dict(pages),
            'most_loved': most_loved,
            'rest': rest,
        },
        RequestContext(request)
    )


def nonprofit(request):

    form_busn = BusinessForm()
    form_nonp = NonprofitForm()
    active = None
    max_pages = 12

    if request.method == 'POST' and request.user.get_pages().count() >= max_pages:
        messages.warning(request, 'Sorry only 12 pages are allowed')
    if request.method == 'POST' and request.POST.get('type', None) and request.user.get_pages().count() < max_pages:
        if request.POST.get('type', None) == 'NP':
            active = 'Nonprofit'
            form = NonprofitForm(data=request.POST)
            form_nonp = form
        else:
            active = "Business"
            form = BusinessForm(data=request.POST)
            form_busn = form
        if form.is_valid() and request.user.get_pages().count() < max_pages:
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            # nullify form
            active = None
            form = PageForm()
            form_busn = BusinessForm()
            form_nonp = NonprofitForm()

    pages = Pages.objects.filter(type='NP')

    # group by cats
    c = 0
    row = defaultdict(list)
    gp = defaultdict(list)
    for page in pages:
        # grouping by rows for template [4 in row]
        row[page.category].append(page)
        c = len(row[page.category])
        if c % 4 == 0:
            random.shuffle(row[page.category])
            gp[page.category].append(row[page.category])
            row[page.category] = []

    for k, v in row.items():
        if k not in gp:
            gp[k] = [v]
        else:
            if v not in gp[k]:
                gp[k].append(v)

    pages = gp

    return render_to_response(
        'pages/nonprofit.html',
        {
            'form_busn': form_busn,
            'form_nonp': form_nonp,
            'pages': dict(pages),
            'active': active,
        },
        RequestContext(request)
    )


def love_count(request):
    data = {'status': 'FAIL'}
    if request.method == 'POST':
        page_id = request.POST.get('page_id')
        vote = request.POST.get('vote')
        if page_id:
            try:
                page = Pages.objects.get(id=int(page_id))
                if vote == 'up':
                    # if BUSINESS
                    loves_limit = page.loves_limit
                    if page.type == 'BS' \
                            and loves_limit <= 0:
                        # go away and wait for love
                        PageLoves.objects.create(user=request.user,page=page,status='Q').save()
                        data['status'] = 'OK'
                        data['loved'] = page.get_lovers_active_count()
                    else:
                        page.loves = page.get_lovers().count() + 1
                        #page.users_loved.add(request.user)
                        PageLoves.objects.create(user=request.user,page=page).save()
                        if page.type == 'BS':
                            page.loves_limit = page.loves_limit - 1
                        page.save()
                        data['status'] = 'OK'
                        data['loved'] = page.get_lovers_active_count()
                if vote == 'down':
                    page.loves = page.get_lovers().count() - 1
                    if page.type == 'BS' \
                            and request.user in page.get_lovers_active():
                        page.loves_limit = page.loves_limit + 1
                    PageLoves.objects.filter(user=request.user,page=page).delete()
                    #page.users_loved.remove(request.user)
                    page.save()
                    data['status'] = 'OK'
                    data['loved'] = page.get_lovers_active_count()
            except Pages.DoesNotExist:
                pass
    return HttpResponse(json.dumps(data), "application/json")


def page_browsing(request, page_type='business'):
    data = {'status': 'OK'}

    if page_type == "nonprofit":
        filter_labels = [filtr[0] for filtr in NONPROFIT_CATEGORY
                         if Pages.objects.filter(category=filtr[0]).count()]
        labels = [filtr[0] for filtr in NONPROFIT_CATEGORY]
        pages = Pages.objects.filter(type='NP').order_by('-loves')
    else:
        filter_labels = [filtr[0] for filtr in BUSINESS_CATEGORY
                         if Pages.objects.filter(category=filtr[0]).count()]
        labels = [filtr[0] for filtr in BUSINESS_CATEGORY]
        pages = Pages.objects.filter(type='BS').order_by('-loves')

    if request.method == 'GET':
        ajax = request.GET.get('ajax', None)
        filters = request.GET.getlist('filters[]', None)
        if filters:
            filter_cats = []
            for filtr in filters:
                filter_cats.append(labels[int(filtr)])
            pages = pages.filter(category__in=filter_cats).order_by('-loves')

    # grouping by rows for template [4 in row]
    n = 0
    col = 2
    grouped_pages = []
    row = []
    for page in pages:
        n += 1
        row.append(page)
        if n % col == 0 or n == pages.count():
            grouped_pages.append(row)
            row = []

    pages = grouped_pages

    if filters and ajax:
        data['html'] = render_to_string(
            'pages/pages.html',
            {
            'pages': pages,
            },
            RequestContext(request)
        )
        return HttpResponse(json.dumps(data), "application/json")

    return render_to_response(
        'pages/browse.html',
        {
            'pages': pages,
            'filters': filter_labels,
            'page_type': page_type,
        },
        RequestContext(request)
    )


@login_required
def update(request):
    data = {'status': 'FAIL'}
    if request.method == 'POST' and 'page_id' in request.POST:
        page_id = request.POST.get('page_id')
        content = request.POST.get('content')
        try:
            page = Pages.objects.get(id=int(page_id))
            if request.user in page.get_admins():
                post = PagePost(user=request.user, content=content, page=page)
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


@login_required
def feedback(request):
    data = {'status': 'FAIL'}
    if request.method == 'POST' and 'page_id' in request.POST:
        page_id = request.POST.get('page_id')
        content = request.POST.get('content')
        rating = request.POST.get('rating')
        try:
            page = Pages.objects.get(id=int(page_id))
            if rating and not request.user.posted_review_for(page):
                post = FeedbackPost(user=request.user, content=content, page=page, rating=rating)
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
    data = {'status': 'FAIL'}
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
                                    'items': items,
                                    'page': page,
                                    }, context_instance=RequestContext(request))
    data['status'] = 'OK'
    return HttpResponse(json.dumps(data), "application/json")


def list_feedback(request, slug=None):
    data = {'status': 'FAIL'}
    if not slug:
        HttpResponse(json.dumps(data), "application/json")
    if slug:
        try:
            page_obj = Pages.objects.get(username=slug)
            items = page_obj.get_feedback().order_by('-date')
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
                                    'items': items,
                                    'page': page,
                                    }, context_instance=RequestContext(request))
    data['status'] = 'OK'
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def settings(request, slug=None):
    from django.conf import settings
    active = 'basics'
    error = ''
    love_error = ''

    stripe_error = ''
    stripe.api_key = settings.STRIPE_API_KEY
    bids = Bids.objects.filter(status=1).order_by('-amount')
    pickle_str = cPickle.dumps(bids[:3])
    old_three = cPickle.loads(pickle_str)
    if bids.count() > 2:
        min_bid = bids[2].amount + 10
    else:
        min_bid = 10

    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404

    now = timezone.now()
    nextMonday = now.date() + dateclass.timedelta(7 - now.weekday())
    endWeek = now.date() + dateclass.timedelta(13 - now.weekday())
    day = now.isoweekday() #5
    hour = now.hour #4pm
    mint = now.minute
    friday = now.date() + dateclass.timedelta(4 - now.weekday())
    closing = dateclass.datetime(friday.year, friday.month, friday.day, 17, 00, tzinfo=pytz.timezone('US/Eastern'))
    #if (mint > 19 and mint < 30) or (mint > 49 and mint <= 59):
    if now > closing:
        show_bids = False
    else:
        show_bids = True

    # check permissions
    if request.user.check_option('pages_admins__%s' % page.id) \
            or request.user.check_option('pages_basics__%s' % page.id) \
            or request.user.check_option('pages_loves__%s' % page.id):
                if request.user.check_option('pages_loves__%s' % page.id):
                    active = 'loves'
                if request.user.check_option('pages_admins__%s' % page.id):
                    active = 'admins'
                if request.user.check_option('pages_basics__%s' % page.id):
                    active = 'basics'
    else:
        raise Http404

    form = PageSettingsForm(instance=page)
    if request.method == 'POST':
        amount = 0
        lamount = 0
        token = request.POST.get('stripeToken_bids', None)
        ltoken = request.POST.get('stripeToken_loves', None)
        bid = request.POST.get('bid_value', None)
        if bid:
            amount = int(bid.strip().replace('$',''))
        active = request.POST.get('active', None)
        last4 = request.POST.get('last4', None)
        ctype = request.POST.get('ctype', None)
        loves = request.POST.get('loves_value', None)
        if loves:
            lamount = int(loves.strip().replace('$',''))
        # adding card info
        if 'cancel_bid' in request.POST:
            bid = page.get_max_bid()
            if bid:
                if bid.user == request.user:
                    bid.delete()
                else:
                    error = "This bid has not been placed by you"
        elif token or ltoken:
            if ltoken:
                try:
                    if request.user.is_lcustomer_for(page):
                        stripe_id = page.get_love_stripe_id(request.user)
                        customer = stripe.Customer.retrieve(stripe_id)
                        customer.card = ltoken
                        customer.save()
                        db_customer = page.get_lcustomer_for(request.user)
                        db_customer.last4 = last4
                        db_customer.type = ctype
                        db_customer.save()
                    else:
                        customer = stripe.Customer.create(
                            card=ltoken,
                            description=page.name
                        )
                        customer = Customers(user=request.user, page=page, stripe_id=customer.id, section='L')
                        customer.last4 = last4
                        customer.type = ctype
                        customer.save()
                except stripe.CardError, e:
                    body = e.json_body
                    err = body['error']
                    stripe_error = err.get('message', 'Card was declined')
                except:
                    stripe_error = 'An error occurred while processing your card'
            else:
                try:
                    if request.user.is_customer_for(page):
                        stripe_id = page.get_stripe_id_for(request.user)
                        customer = stripe.Customer.retrieve(stripe_id)
                        customer.card = token
                        customer.save()
                        db_customer = page.get_customer_for(request.user)
                        db_customer.last4 = last4
                        db_customer.type = ctype
                        db_customer.save()
                    else:
                        customer = stripe.Customer.create(
                            card=token,
                            description=page.name
                        )
                        customer = Customers(user=request.user, page=page, stripe_id=customer.id, section='B')
                        customer.last4 = last4
                        customer.type = ctype
                        customer.save()
                except stripe.CardError, e:
                    body = e.json_body
                    err = body['error']
                    stripe_error = err.get('message', 'Card was declined')
                except:
                    stripe_error = 'An error occurred while processing your card'
        # bidding
        elif amount or lamount:
            # loves
            if lamount and 'submit_loves' in request.POST:
                # if mod 100
                if lamount%100 == 0:
                    ch_amount = lamount * 100
                    if not page.exempt:
                        stripe_id = page.get_love_stripe_id(request.user)
                    try:
                        if not page.exempt:
                            stripe.Charge.create(
                                amount=ch_amount, # 1500 - $15.00 this time
                                currency="usd",
                                customer=stripe_id,
                                description="Loves for %s, user: %s" % (page.name, request.user)
                            )
                            Summary.objects.create(user=request.user, page=page, amount=lamount, type='L')
                        page.loves_limit = page.loves_limit + lamount
                        users_inq = PageLoves.objects.filter(page=page,status='Q')[:lamount]
                        for quser in users_inq:
                            quser.status='A'
                            quser.save()
                            page.loves_limit = page.loves_limit - 1
                        page.save()
                    except:
                        love_error = 'An error occurred while processing your card'
            # bids
            if amount and 'submit_bids' in request.POST:
                ebid = page.get_max_bid()
                if ebid:
                    bid = ebid
                else:
                    bid = Bids( page = page)
                # do not process bids lower than previous
                if bid.amount < amount:
                    bid.amount = amount
                    bid.user = request.user
                    # save only for permitted period
                    if show_bids and \
                            not page.is_disabled and \
                            amount >= min_bid:
                        # save bid
                        bid.save()
                        # find all outbidders
                        outbs = Bids.objects.filter(status=1, amount__lt=bid.amount)
                        max_three = bids[:3]
                        for outb in outbs:
                            # if in old
                            if outb in old_three \
                                    and outb not in max_three:
                                    # but not in new
                                pr = PageRequest(from_page = outb.page, to_page = outb.page, type = 'BO')
                                pr.save()
                else:
                    error = "Can't process bid lower than previous"
        # just form
        else:
            form = PageSettingsForm(data=request.POST, instance=page)
            if form.is_valid():
                form.save()
    return render_to_response(
            "pages/settings.html",
                {
                    'page': page,
                    'form': form,
                    'active': active,
                    'min_bid': min_bid,
                    'stripe_error': stripe_error,
                    'show_bids': show_bids,
                    'error': error,
                    'nextm': nextMonday,
                    'startw': nextMonday,
                    'endw': endWeek,
                    'closing': closing,
                    'love_error': love_error,
                },
                RequestContext(request)
            )


@login_required
def settings_admins(request, slug=None):
    data = {'status': 'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        admin_username = request.POST.get('admin_username', None)
        removing = request.POST.get('remove', None)
        adding = request.POST.get('add', None)
        option = request.POST.get('option', None)
        if option:
            option, admin_username = option.split('__')
        try:
            admin = UserProfile.objects.get(username=admin_username)
            if adding:
                page.admins.add(admin)
            if removing:
                page.admins.remove(admin)
                options = admin.find_options('pages', page)
                options.delete()
            if option:
                if admin.check_option("%s__%s" % (option, page.id)):
                    admin.set_option("%s__%s" % (option, page.id), False)
                else:
                    admin.set_option("%s__%s" % (option, page.id), True)
            data['status'] = 'OK'
            data['html'] = render_to_string("pages/settings_admins.html",
                                            {
                                            'page': page,
                                            }, RequestContext(request))
        except:
            HttpResponse(json.dumps(data), "application/json")
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def delete_page(request, slug=None):
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    if 'delete_page' in request.POST:
        password = request.POST.get('confirm_password', None)
        if check_password(password, request.user.password):
            if page.user == request.user and request.user.check_option('pages_delete__%s' % page.id):
                delta = dateclass.timedelta(days=7)
                #delta = dateclass.timedelta(minutes=30)
                page.for_deletion = timezone.now() + delta
                page.save()
                #page.delete()
            else:
                messages.error(request, 'You don\'t have sufficient permissions.')
                return redirect('pages.views.settings', slug=page.username)
        else:
            messages.error(request, 'Wrong password.')
            return redirect('pages.views.settings', slug=page.username)
    return redirect('pages.views.main')


@login_required
def prevent_deletion(request, slug=None):
    data = {'status': 'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    page.for_deletion = None
    page.save()
    data['status'] = 'OK'
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def page_content(request, slug=None):
    data = {'status': 'OK'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    content = request.POST.get('content', '')
    page.content = content
    page.save()
    data['html'] = render_to_string("pages/page_content.html",
                                    {
                                    'page': page,
                                    }, RequestContext(request))
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def send_friend_request(request, slug=None):
    data = {'status': 'OK'}
    from_page = None
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        page_id = request.POST.get('page_id', None)
        if page_id:
            try:
                from_page = Pages.objects.get(id=int(page_id))
            except Pages.DoesNotExist:
                raise Http404
    user_pages = request.user.get_community_pages()
    if page in user_pages:
        # remove current
        user_pages.remove(page)
    for one_page in user_pages[:]:
        # remove friends
        if one_page in page.get_friends():
            user_pages.remove(one_page)
    topage_requests = [one_page.from_page for one_page in page.get_requests()]
    for one_page in topage_requests:
        # remove already pending requests
        if one_page in user_pages:
            user_pages.remove(one_page)
    if len(user_pages) == 1 and not from_page:
        from_page = user_pages[0]
    if not from_page:
        if user_pages:
            data['pages'] = render_to_string("pages/page_choose.html",
                                             {
                                             'pages': user_pages,
                                             }, RequestContext(request))
        else:
            data['status'] = 'FAIL'
    else:
        # check if request exist or in friends
        topage_requests = [one_page.from_page for one_page in page.get_requests()]
        if from_page in page.get_friends() or from_page in topage_requests:
            data['status'] = 'FAIL'
            return HttpResponse(json.dumps(data), "application/json")
        page_request = page.to_page.create(from_page=from_page,
                                           to_page=page)

    return HttpResponse(json.dumps(data), "application/json")


@login_required
def remove_friend_page(request, slug=None):
    data = {'status': 'OK'}
    friend = None
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        page_id = request.POST.get('page_id', None)
        if page_id:
            try:
                friend = Pages.objects.get(id=int(page_id))
            except Pages.DoesNotExist:
                raise Http404
    user_page_friends = request.user.get_community_pages_friends(page)
    if len(user_page_friends) == 1 and not friend:
        friend = user_page_friends[0]
    if not friend:
        data['pages'] = render_to_string("pages/page_choose.html",
                                         {
                                         'pages': user_page_friends,
                                         }, RequestContext(request))
    else:
        page.friends.remove(friend)
        PageRequest.objects.filter(to_page=page, from_page=friend).delete()
        PageRequest.objects.filter(to_page=friend, from_page=page).delete()
        data['pages_count'] = len(user_page_friends) - 1
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def accept_friend_request(request, slug=None, request_id=None):
    data = {'status': 'OK'}
    if request_id:
        try:
            page_request = PageRequest.objects.get(id=int(request_id))
            page_request.accept()
        except PageRequest.DoesNotExist:
            raise Http404
    return redirect(page_request.to_page.get_absolute_url())


@login_required
def decline_friend_request(request, slug=None, request_id=None):
    data = {'status': 'OK'}
    if request_id:
        try:
            page_request = PageRequest.objects.get(id=int(request_id))
            page_request.decline()
        except PageRequest.DoesNotExist:
            raise Http404
    return redirect(page_request.to_page.get_absolute_url())


@login_required
def hide_friend_request(request, slug=None, request_id=None):
    data = {'status': 'OK'}
    if request_id:
        try:
            page_request = PageRequest.objects.get(id=int(request_id))
            page_request.hide()
        except PageRequest.DoesNotExist:
            raise Http404
    return redirect(page_request.from_page.get_absolute_url())


@login_required
def accept_community_request(request, slug=None, request_id=None):
    data = {'status': 'OK'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    if request_id:
        try:
            member = Membership.objects.get(id=int(request_id))
            member.confirm()
            data['html'] = render_to_string("pages/micro/_community_list.html",
                                            {
                                            'page': page,
                                            }, RequestContext(request))
        except Membership.DoesNotExist:
            raise Http404
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def decline_community_request(request, slug=None, request_id=None):
    data = {'status': 'OK'}
    if request_id:
        try:
            member = Membership.objects.get(id=int(request_id))
            member.decline()
        except Membership.DoesNotExist:
            raise Http404
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def friends_position(request, slug=None):
    data = {'status': 'OK'}
    if request.method == 'POST':
        position_bgn = request.POST.get('position_bgn')
        position_end = request.POST.get('position_end')
        friend_id = request.POST.get('friend_id')
        if friend_id:
            try:
                #import pdb;pdb.set_trace()
                page = Pages.objects.get(username=slug)
                friend = Pages.objects.get(id=int(friend_id))
                try:
                    obj = PagePositions.objects.get(to_page=page, from_page=friend)
                except:
                    # something wrong with positioning,
                    # but we will save new position anyway
                    obj = PagePositions(to_page=page, from_page=friend)
                obj.position = position_end
                obj.save()
                if position_bgn < position_end:
                    positions = PagePositions.objects.filter(to_page=page,
                                                             position__gte=position_bgn,
                                                             position__lte=position_end,
                                                             from_page__type=friend.type).exclude(id=obj.id)
                    positions.update(position=F('position') - 1)
                elif position_bgn > position_end:
                    positions = PagePositions.objects.filter(to_page=page,
                                                             position__gte=position_end,
                                                             position__lte=position_bgn,
                                                             from_page__type=friend.type).exclude(id=obj.id)
                    positions.update(position=F('position') + 1)
                # this fix only for broken positioning
                positions.filter(position__lt=0).update(position=0)
            except:
                raise Http404

    return HttpResponse(json.dumps(data), "application/json")


@login_required
def community_check(request, slug=None):
    data = {'status': 'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    name = request.POST.get('name', None)
    checked = request.POST.get('checked', None)
    if checked == 'true':
        checked = True
    else:
        checked = False
    if name == 'employees_checkbox':
        page.has_employees = checked
        page.save()
        data['status'] = 'OK'
    if name == 'interns_checkbox':
        page.has_interns = checked
        page.save()
        data['status'] = 'OK'
    if name == 'volunteers_checkbox':
        page.has_volunteers = checked
        page.save()
        data['status'] = 'OK'
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def community_text(request, slug=None):
    data = {'status': 'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    content = request.POST.get('content', None)
    parent_id = request.POST.get('parent_id', None)
    if parent_id == 'employees_div':
        page.text_employees = content
        page.save()
        data['status'] = 'OK'
    if parent_id == 'interns_div':
        page.text_interns = content
        page.save()
        data['status'] = 'OK'
    if parent_id == 'volunteers_div':
        page.text_volunteers = content
        page.save()
        data['status'] = 'OK'
    if data['status'] == 'OK':
        data['html'] = render_to_string("pages/micro/_community_info.html",
                                        {
                                        'content': content,
                                        }, RequestContext(request))
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def community_date(request, slug=None):
    data = {'status': 'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    date = request.POST.get('date', None)
    date_type = request.POST.get('date_type', None)
    member_id = request.POST.get('id', None)
    try:
        member = Membership.objects.get(id=member_id)
    except Membership.DoesNotExist:
        raise Http404
    if date:
        date = datetime.strptime(date, "%m/%Y")
        if date_type == 'from_date':
            member.from_date = date
        if date_type == 'to_date':
            member.is_present = False
            member.to_date = date
        member.save()
        data['status'] = 'OK'
        data['html'] = datetime.strftime(date, "%b. %Y")
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def page_members(request, slug=None, member_id=None):
    data = {'status': 'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    member = None
    new = False
    member_type = request.POST.get('member_type', None)
    from_date = request.POST.get('from_date', None)
    to_date = request.POST.get('to_date', None)
    user = request.user
    delete_member = request.POST.get('delete', None)
    if member_id:
        try:
            member = Membership.objects.get(id=member_id)
        except Membership.DoesNotExist:
            member = None
    if delete_member:
        if user == member.get_user():
            member.delete()
            data['status'] = 'OK'
            data['id'] = member_id
    else:
        if from_date and member_type:
            from_date = datetime.strptime(from_date, "%m/%Y")
            if to_date:
                to_date = datetime.strptime(to_date, "%m/%Y")
            if not member:
                member = Membership()
                new = True
                member.user = user
                member.page = page
            member.type = member_type
            member.from_date = from_date
            if to_date:
                member.to_date = to_date
                member.is_present = False
            else:
                member.is_present = True
            try:
                if user == member.get_user():
                    if member.get_user().check_option('pages_removed__%s__%s' % (page.id, member.type)):
                        date_old = member.get_user().check_option('pages_removed__%s__%s' % (page.id, member.type))
                        date1 = datetime.strptime(date_old, "%m/%d/%Y")
                        date2 = datetime.today()
                        diff = date2 - date1
                        if diff.days >= 30:
                            member.get_user().remove_option('pages_removed__%s__%s' % (page.id, member.type))
                    if not (member.get_user().check_option('pages_removed__%s__%s' % (page.id, member.type)) and new):
                        member.save()
                        data['status'] = 'OK'
                        data['redirect'] = reverse('user-loves', args=(request.user,))
                        data['html'] = render_to_string("pages/micro/_community_list.html",
                                                        {
                                                        'page': page,
                                                        }, RequestContext(request))
                    else:
                        data['message'] = 'Previous request denied. Unable to make new request for %s days.' % (30 - diff.days)

            except:
                pass
    return HttpResponse(json.dumps(data), "application/json")


def images(request, slug, rows_show=4):
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404

    ctype = ContentType.objects.get_for_model(Pages)
    qs = Image.objects.filter(owner_type=ctype, owner_id=page.id)
    manage_perm = request.user.is_authenticated() \
        and request.user.check_option('pages_photos__%s' % page.id) \
        and request.user in page.get_admins()

    if request.method == 'POST' \
        and 'album_image' in request.POST \
            and manage_perm:
        album_form = ImageForm(request.POST, request.FILES)
        if album_form.is_valid():
            image = album_form.save(page)
            image.make_activity()
            image.generate_thumbnail(200, 200)
            # try:
            #     pil_object = pilImage.open(image.image.path)
            #     w, h = pil_object.size
            #     x, y = 0, 0
            #     if w > h:
            #         x, y, w, h = int((w-h)/2), 0, h, h
            #     elif h > w:
            #         x, y, w, h = 0, int((h-w)/2), w, w
            #     new_pil_object = pil_object \
            #         .crop((x, y, x+w, y+h)) \
            #         .resize((200, 200))
            #     new_pil_object.save(image.image.thumb_path)
            # except:
            #     pass
            return redirect('pages.views.images', slug=page.username)
    else:
        album_form = ImageForm()

    return render_to_response(
        'pages/images.html',
        {
            'page': page,
            'album_form': album_form,
            'image_rows': qs.get_rows(0, rows_show),
            'total_rows': qs.total_rows(),
            'photos_count': qs.count(),
            'manage_perm': manage_perm,
        },
        RequestContext(request)
    )


def images_ajax(request, slug):
    if not request.is_ajax():
        raise Http404

    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404

    method = request.REQUEST.get('method', None)
    if method not in ['more', 'activity', 'delete', 'change_position']:
        raise Http404

    ctype = ContentType.objects.get_for_model(Pages)
    qs = Image.objects.filter(owner_type=ctype, owner_id=page.id)
    manage_perm = request.user.is_authenticated() \
        and request.user in page.get_admins() \
        and request.user.check_option('pages_photos__%s' % page.id)

    if method in ['activity', 'delete', 'change_position'] and not manage_perm:
        raise Http404

    data = {}
    try:
        if method == 'more':
            try:
                row = int(request.REQUEST.get('row', None))
            except (TypeError, ValueError), e:
                return HttpResponseBadRequest('Bad row was received.')
            data['total_rows'] = qs.total_rows()
            if row >= data['total_rows']:
                return HttpResponseBadRequest('Row larger than total_rows.')
            data['html'] = render_to_string('images/li.html', {
                'rows': qs.get_row(row),
                'manage_perm': manage_perm,
            }, context_instance=RequestContext(request))
        elif method == 'activity':
            try:
                image = qs.get(pk=request.REQUEST.get('pk', None))
            except Image.DoesNotExist:
                return HttpResponseBadRequest('Bad PK was received.')
            image.make_activity()
            page = Pages.objects.get(pk=page.pk)
        elif method == 'delete':
            try:
                row = int(request.REQUEST.get('row', None)) - 1
            except (TypeError, ValueError), e:
                return HttpResponseBadRequest('Bad row was received.')
            try:
                image = qs.get(pk=request.REQUEST.get('pk', None))
            except UserImages.DoesNotExist:
                return HttpResponseBadRequest('Bad PK was received.')
            image.delete()
            if image.activity == True:
                page = Pages.objects.get(pk=page.pk)
            if row < qs.total_rows():
                image_row = qs.get_row(row)[-1:]
                manage_perm = request.user in page.get_admins() \
                    and request.user.check_option('pages_photos__%s' % page.id)
                data['html'] = render_to_string('images/li.html', {
                    'rows': image_row,
                    'manage_perm': manage_perm,
                }, context_instance=RequestContext(request))
        elif method == 'change_position':
            try:
                obj = qs.get(pk=request.REQUEST.get('pk', None))
                if obj.activity:
                    return HttpResponseBadRequest('Image with pk is actively.')
            except Image.DoesNotExist as e:
                return HttpResponseBadRequest('Bad pk was received.')
            try:
                instead = qs.get(pk=request.REQUEST.get('instead', None))
                if instead.activity:
                    return HttpResponseBadRequest('Image with instead is actively.')
            except Image.DoesNotExist as e:
                return HttpResponseBadRequest('Bad instead was received.')
            obj.change_position(obj.rating, instead.rating)
        else:
            raise Http404
        data['positions'] = qs.get_positions()
        data['thumb_src'] = '/' + page.photo.thumb_name
        data['photos_count'] = qs.count()
    except Exception as e:
        data['status'] = 'fail'
    else:
        data['status'] = 'ok'
    return HttpResponse(json.dumps(data), "application/json")


def images_comments_ajax(request, slug):
    if not request.is_ajax():
        raise Http404

    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404

    method = request.REQUEST.get('method', None)
    if method not in ['create', 'list', 'delete']:
        raise Http404

    ctype = ContentType.objects.get_for_model(Pages)
    qs = Image.objects.filter(owner_type=ctype, owner_id=page.id)
    manage_perm = request.user.is_authenticated() \
        and request.user in page.get_admins() \
        and request.user.check_option('pages_photos__%s' % page.id)

    try:
        image = qs.get(pk=request.REQUEST.get('pk', None))
    except Image.DoesNotExist as e:
        return HttpResponseBadRequest('Bad pk was received.')

    if method in ['delete'] and not manage_perm:
        raise Http404

    data = {}
    try:
        if method == 'create':
            try:
                message = request.REQUEST['message']
            except KeyError:
                return HttpResponseBadRequest("Comment wasn't received.")
            comment = ImageComments.objects.create(
                image=image,
                owner=request.user,
                message=message
            )
        elif method == 'list':
            pass
        elif method == 'delete':
            try:
                comment = image.comments.get(pk=request.REQUEST.get('comment_pk', None))
            except ImageComments.DoesNotExist as e:
                return HttpResponseBadRequest('Bad comment_pk was received.')
            comment.delete()
        else:
            raise Http404
        data['comments'] = render_to_string('images/li_comment.html', {
            'page': page,
            'image': image,
            'comments': image.comments.all(),
            'manage_perm': manage_perm,
        }, context_instance=RequestContext(request))
    except Exception as e:
        data['status'] = 'fail'
    else:
        data['status'] = 'ok'
    return HttpResponse(json.dumps(data), "application/json")


def count_agrees(request, item_id):
    data = {'status': 'FAIL'}
    try:
        post = FeedbackPost.objects.get(id=item_id)
    except FeedbackPost.DoesNotExist:
        raise Http404
    if request.user not in post.get_agreed_list():
        #post.agrees += 1
        post.agreed.add(request.user)
        post.save()
        data['status'] = 'OK'
    else:
        post.agreed.remove(request.user)
        data['status'] = 'change'
    return HttpResponse(json.dumps(data), "application/json")


def count_disagrees(request, item_id):
    data = {'status': 'FAIL'}
    try:
        post = FeedbackPost.objects.get(id=item_id)
    except FeedbackPost.DoesNotExist:
        raise Http404
    if request.user not in post.get_disagreed_list():
        #post.disagrees += 1
        post.disagreed.add(request.user)
        post.save()
        data['status'] = 'OK'
    else:
        post.disagreed.remove(request.user)
        data['status'] = 'change'
    return HttpResponse(json.dumps(data), "application/json")


def add_events(request, slug):
    data = {'status': 'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    event_id = request.POST.get('id', None)
    name = request.POST.get('name', None)
    date = request.POST.get('start', None)
    #allday = request.POST.get('allday',None)
    delete = request.POST.get('del', None)
    desc = request.POST.get('desc', None)
    end = request.POST.get('end', None)
    coords = request.POST.get('coords', None)
    privacy = request.POST.get('privacy', 'public')
    pages = request.POST.get('pages', None)
    clone = request.POST.get('clone', None)
    allow_commenting = request.POST.get('allow_commenting', None)
    allow_sharing = request.POST.get('allow_sharing', None)
    if date:
        date_beg = dateutil.parser.parse(date)
        if name:
            if event_id:
                event = page.events_set.get(id=event_id)
            else:
                event = Events(page=page)
            event.name = name
            event.date = date_beg
            if end:
                time1 = dateutil.parser.parse(end)
                event.date_end = time1
            if desc:
                event.description = desc
            if privacy != 'public':
                privacies = json.loads(privacy)
                pr = [pr[0].upper() for pr in privacies]
                pr = ','.join(pr)
                event.privacy = pr
            else:
                event.privacy = 'P'
            if allow_commenting == 'False':
                event.allow_commenting = False
            else:
                event.allow_commenting = True
            if allow_sharing == 'False':
                event.allow_sharing = False
            else:
                event.allow_sharing = True
            event.save()
            if coords:
                coords = json.loads(coords)
                event.remove_locations()
                for coord in coords:
                    loc = Locations(lat=coord.get('lat'), lng=coord.get('lng'), event=event)
                    loc.save()
            else:
                locs = Locations.objects.filter(event=event)
                locs.delete()
            if pages:
                pages = json.loads(pages)
                pages = set(pages)
                for pg in pages:
                    page_name = pg.strip()
                    if page_name:
                        try:
                            spage = Pages.objects.get(username=page_name)
                            if not clone:
                                req_count = PageRequest.objects.filter(from_page=page, to_page=spage, type='ER', event=event).count()
                                if not req_count:
                                    pr = PageRequest(from_page=page, to_page=spage, type='ER', event=event)
                                    pr.save()
                            else:
                                event.tagged.add(spage)
                        except Pages.DoesNotExist:
                            pass
            if delete:
                if event.page == page:
                    event.delete()
            data['status'] = 'OK'
            data['id'] = event.id
    return HttpResponse(json.dumps(data), "application/json")


def get_events(request, slug):
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    events = page.tagged_in.all()
    data = []
    roles = request.user.get_user_roles_for(page)
    for event in events:
        classes = ''
        append = False
        ev = {
            'id': event.id,
            'owner_id': event.page.id,
            'title': event.name,
            'start': event.date.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if event.date_end:
            ev['end'] = event.date_end.strftime("%Y-%m-%d %H:%M:%S")
        if event.description:
            ev['description'] = event.description
        if event.get_locations().count():
            ev['coords'] = event.get_locations_list()
        for privacy in event.get_privacy():
            if privacy == 'P':
                classes = classes + 'event-public '
            if privacy == 'A':
                classes = classes + 'event-admins '
            if privacy == 'E':
                classes = classes + 'event-employees '
            if privacy == 'I':
                classes = classes + 'event-interns '
            if privacy == 'V':
                classes = classes + 'event-volunteers '
        if event.get_tagged_pages():
            links = ["<a href=\"%s\">%s</a>" % (a.get_absolute_url(), a.name) for a in event.get_tagged_pages(page)]
            page_names = [p.username for p in event.get_tagged_pages()]
            ev['tagged'] = ", ".join(links)
            ev['page_names'] = ", ".join(page_names)
            classes = classes + 'event-shared '
        if classes:
            ev['className'] = classes
            ev['privacy'] = ",".join(event.get_privacy())
        #comments
        from django.contrib.comments.forms import CommentForm
        from django.contrib.contenttypes.models import ContentType
        from django.contrib import comments
        from django.conf import settings

        comment_list = comments.get_model().objects.filter(
            content_type=ContentType.objects.get_for_model(Events),
            object_pk=event.pk,
            site__pk=settings.SITE_ID,
            is_removed=False,
        )
        ev['comment_list'] = render_to_string('comments/list.html',
                                              {
                                              'comment_list': comment_list,
                                              }, RequestContext(request))
        ev['comment_form'] = render_to_string('comments/form_event.html',
                                              {
                                              'item': event,
                                              'form': CommentForm(event),
                                              }, RequestContext(request))
        ev['allow_commenting'] = event.allow_commenting
        ev['allow_sharing'] = event.allow_sharing
        for role in roles:
            if role in event.get_privacy():
                append = True
        if append:
            data.append(ev)
    return HttpResponse(json.dumps(data), "application/json")


def change_event(request, slug):
    data = {'status': 'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    event_id = request.POST.get('id', None)
    start = request.POST.get('start', None)
    end = request.POST.get('end', None)
    delete = request.POST.get('del', None)
    try:
        event = page.events_set.get(id=event_id)
    except Events.DoesNotExist:
        raise Http404
    if start:
        start = dateutil.parser.parse(start)
        event.date = start
        event.save()
        data['status'] = 'OK'
    if end:
        end = dateutil.parser.parse(end)
        event.date_end = end
        event.save()
        data['status'] = 'OK'
    if delete:
        if event.page == page:
            event.delete()
            data['status'] = 'OK'

    return HttpResponse(json.dumps(data), "application/json")


def post_update_change(request, slug):
    data = {'status': 'OK'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    value = request.POST.get('value', None)
    if value == 'true':
        page.post_update = True
        page.save()
    if value == 'false':
        page.post_update = False
        page.save()
    return HttpResponse(json.dumps(data), "application/json")


def event_comments(request, slug):
    data = {'status': 'OK'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    event_id = request.POST.get('event_id', None)
    if event_id:
        try:
            event = Events.objects.get(id=int(event_id))
            data['html'] = render_to_string('comments/form.html',
                                            {
                                            'item': event,
                                            }, RequestContext(request))
        except Events.DoesNotExist:
            raise Http404

    return HttpResponse(json.dumps(data), "application/json")


def share_event(request, slug):
    data = {'status': 'OK'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    event_id = request.POST.get('event_id', None)
    share_to = request.POST.get('share_to', None)
    try:
        event = Events.objects.get(id=int(event_id))
        content = mark_safe("""Check out <i>%s</i>, an event from <a href=\"%s\">%s</a>.""" % (event.name, page.get_absolute_url(), page.name))
        if event.description:
            content = content + "\n Event Description: %s" % event.description
    except Events.DoesNotExist:
        raise Http404
    if share_to and share_to != 'profile':
        try:
            share_page = Pages.objects.get(id=int(share_to))
            post = PagePost(user=request.user, content=content, page=share_page)
            post.save()
        except:
            data['status'] = 'FAIL'
            return HttpResponse(json.dumps(data), "application/json")
    else:
        post = ContentPost(content=content, user=request.user, user_to=request.user, type='P')
        #post = SharePost(user = request.user, user_to=request.user , content = content )
        post.save()

    return HttpResponse(json.dumps(data), "application/json")


def card_form(request, slug):
    if request.method == 'POST' and not request.user.is_customer():
        import pdb
        pdb.set_trace()
        # set your secret key: remember to change this to your live secret key in production
        # see your keys here https://manage.stripe.com/account
        stripe.api_key = "GfdATJpLDgriMZ66PPrK0Kf9XuCsZU9w"

        # get the credit card details submitted by the form
        token = request.POST['stripeToken']

        # create a Customer
        customer = stripe.Customer.create(
            card=token,
            description=request.user.username
        )

        """
        # charge the Customer instead of the card
        stripe.Charge.create(
            amount=1000, # in cents
            currency="usd",
            customer=customer.id
        )
        """
        # save the customer ID in your database so you can use it later
        #save_stripe_customer_id(user, customer.id)
        customer = Customers(user=request.user, stripe_id=customer.id)
        customer.save()

        """
        # later
        customer_id = get_stripe_customer_id(user)

        stripe.Charge.create(
            amount=1500, # $15.00 this time
            currency="usd",
            customer=customer_id
        )
        """

    return render_to_response(
        'pages/card_form.html',
        {
        },
        RequestContext(request)
    )


def start_topic(request, slug):
    data = {'status': 'OK'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        form = PageTopicForm(request.POST)
        topic = form.save(commit=False)
        topic.user = request.user
        topic.page = page
        members = request.POST.getlist('members', None)
        if members:
            members.append("A")
            topic.members = ",".join(members)
        topic.save()


    return HttpResponse(json.dumps(data), "application/json")
