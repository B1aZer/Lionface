from django.http import *
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import F
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

from django.contrib import messages
from django.contrib.auth.hashers import check_password

try:
    import json
except ImportError:
    import simplejson as json


def main(request):

    form_busn = BusinessForm()
    form_nonp = NonprofitForm()
    active = None
    max_pages = 12

    if request.method == 'POST' and request.user.get_pages().count() == max_pages:
        messages.warning(request, 'Sorry only 12 pages are allowed')
    if request.method == 'POST' and request.POST.get('type',None) and request.user.get_pages().count() <= max_pages:
        if request.POST.get('type',None) == 'NP':
            active = 'Nonprofit'
            form = NonprofitForm(data = request.POST)
            form_nonp = form
        else:
            active = "Business"
            form = BusinessForm(data = request.POST)
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

    pages = Pages.objects.filter(type='BS').order_by('?')[:8]

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


def page_browsing(request, page_type='business'):
    data = {'status':'OK'}

    if page_type == "nonprofit":
        filter_labels = [filtr[0] for filtr in NONPROFIT_CATEGORY]
        pages = Pages.objects.filter(type='NP').order_by('-loves')
    else:
        filter_labels = [filtr[0] for filtr in BUSINESS_CATEGORY]
        pages = Pages.objects.filter(type='BS').order_by('-loves')

    if request.method == 'GET':
        filters = request.GET.getlist('filters[]',None)
        if filters:
            filter_cats = []
            for filtr in filters:
                filter_cats.append(filter_labels[int(filtr)])
            pages = pages.filter(category__in=filter_cats).order_by('-loves')

    # grouping by rows for template [4 in row]
    n=0
    col=2
    grouped_pages = []
    row = []
    for page in pages:
        n += 1
        row.append(page)
        if n%col == 0 or n == pages.count():
            grouped_pages.append(row)
            row = []

    pages = grouped_pages

    if filters:
        data['html'] = render_to_string(
                                'pages/pages.html',
                                    {
                                        'pages':pages,
                                    },
                                    RequestContext(request)
                                )
        return HttpResponse(json.dumps(data), "application/json")


    return render_to_response(
        'pages/browse.html',
        {
            'pages':pages,
            'filters':filter_labels,
        },
        RequestContext(request)
    )


@login_required
def update(request):
    data = {'status':'FAIL'}
    if request.method == 'POST' and 'page_id' in request.POST:
        page_id = request.POST.get('page_id')
        content = request.POST.get('content')
        try:
            page = Pages.objects.get(id=int(page_id))
            if request.user in page.get_admins():
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


@login_required
def settings(request, slug=None):
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    # check permissions
    if request.user.check_option('pages_admins__%s' % page.id) \
            or request.user.check_option('pages_basics__%s' % page.id):
                pass
    else:
        raise Http404
    form = PageSettingsForm(instance=page)
    if request.method == 'POST':
        form = PageSettingsForm(data=request.POST, instance=page)
        if form.is_valid():
            form.save()
    return render_to_response(
            "pages/settings.html",
                {
                    'page': page,
                    'form': form,
                },
                RequestContext(request)
            )


@login_required
def settings_admins(request, slug=None):
    data = {'status':'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        admin_username = request.POST.get('admin_username',None)
        removing = request.POST.get('remove',None)
        adding = request.POST.get('add',None)
        option = request.POST.get('option',None)
        if option:
            option, admin_username = option.split('__')
        try:
            admin = UserProfile.objects.get(username=admin_username)
            if adding:
                page.admins.add(admin)
            if removing:
                page.admins.remove(admin)
            if option:
                if admin.check_option("%s__%s" % (option,page.id)):
                    admin.set_option("%s__%s" % (option,page.id),False)
                else:
                    admin.set_option("%s__%s" % (option,page.id),True)
            data['status'] = 'OK'
            data['html'] = render_to_string("pages/settings_admins.html",
                    {
                        'page':page,
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
        password = request.POST.get('confirm_password',None)
        if check_password(password, request.user.password):
            if page.user == request.user and request.user.check_option('pages_delete__%s' % page.id):
                page.delete()
            else:
                messages.error(request, 'You don\'t have sufficient permissions.')
                return redirect('pages.views.settings', slug=page.username)
        else:
            messages.error(request, 'Wrong password.')
            return redirect('pages.views.settings', slug=page.username)
    return redirect('pages.views.main')


@login_required
def page_content(request, slug=None):
    data = {'status':'OK'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    content = request.POST.get('content','')
    page.content = content
    page.save()
    data['html'] = render_to_string("pages/page_content.html",
                    {
                        'page':page,
                    }, RequestContext(request))
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def send_friend_request(request, slug=None):
    data = {'status':'OK'}
    from_page = None
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        page_id = request.POST.get('page_id',None)
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
                        'pages' : user_pages,
                    }, RequestContext(request))
        else:
            data['status']='FAIL'
    else:
        # check if request exist or in friends
        topage_requests = [one_page.from_page for one_page in page.get_requests()]
        if from_page in page.get_friends() or from_page in topage_requests:
            data['status']='FAIL'
            return HttpResponse(json.dumps(data), "application/json")
        page_request = page.to_page.create(from_page = from_page, \
                                        to_page = page)

    return HttpResponse(json.dumps(data), "application/json")


@login_required
def remove_friend_page(request, slug=None):
    data = {'status':'OK'}
    friend = None
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        page_id = request.POST.get('page_id',None)
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
                        'pages' : user_page_friends,
                    }, RequestContext(request))
    else:
        page.friends.remove(friend)
        PageRequest.objects.filter(to_page=page, from_page=friend).delete()
        PageRequest.objects.filter(to_page=friend, from_page=page).delete()
        data['pages_count'] = len(user_page_friends) - 1
    return HttpResponse(json.dumps(data), "application/json")


@login_required
def accept_friend_request(request, slug=None, request_id=None):
    data = {'status':'OK'}
    if request_id:
        try:
            page_request = PageRequest.objects.get(id=int(request_id))
            page_request.accept()
        except PageRequest.DoesNotExist:
            raise Http404
    return redirect(page_request.to_page.get_absolute_url())


@login_required
def decline_friend_request(request, slug=None, request_id=None):
    data = {'status':'OK'}
    if request_id:
        try:
            page_request = PageRequest.objects.get(id=int(request_id))
            page_request.decline()
        except PageRequest.DoesNotExist:
            raise Http404
    return redirect(page_request.to_page.get_absolute_url())


@login_required
def hide_friend_request(request, slug=None, request_id=None):
    data = {'status':'OK'}
    if request_id:
        try:
            page_request = PageRequest.objects.get(id=int(request_id))
            page_request.hide()
        except PageRequest.DoesNotExist:
            raise Http404
    return redirect(page_request.from_page.get_absolute_url())


@login_required
def friends_position(request, slug=None):
    data = {'status':'OK'}
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
                    positions = PagePositions.objects.filter(to_page=page, \
                            position__gte=position_bgn, \
                            position__lte=position_end, \
                            from_page__type=friend.type).exclude(id=obj.id)
                    positions.update(position=F('position') - 1)
                elif position_bgn > position_end:
                    positions = PagePositions.objects.filter(to_page=page,
                            position__gte=position_end, \
                            position__lte=position_bgn, \
                            from_page__type=friend.type).exclude(id=obj.id)
                    positions.update(position=F('position') + 1)
                # this fix only for broken positioning
                positions.filter(position__lt=0).update(position=0)
            except:
                raise Http404



    return HttpResponse(json.dumps(data), "application/json")


@login_required
def community_check(request, slug=None):
    data = {'status':'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    name = request.POST.get('name',None)
    checked = request.POST.get('checked',None)
    if checked =='true':
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
    data = {'status':'FAIL'}
    try:
        page = Pages.objects.get(username=slug)
    except Pages.DoesNotExist:
        raise Http404
    content = request.POST.get('content',None)
    parent_id = request.POST.get('parent_id',None)
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
                        'content':content,
                    }, RequestContext(request))
    return HttpResponse(json.dumps(data), "application/json")





