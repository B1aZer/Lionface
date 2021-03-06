from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render
from django.db.models import Q, Count

try:
    import json
except ImportError:
    import simplejson as json

from account.models import UserProfile
from .models import Alum, School

SCHOOLS_PER_PAGE = 10


@login_required
def home(request):
    profile = UserProfile.objects.get(id=request.user.id)
    alum_schools = School.objects.filter(approved=True, alumni__user=profile)

    if alum_schools:
        alum_school = alum_schools[0]
        alum = Alum.objects.get(user=profile, school=alum_school)
        alum_list = Alum.objects.filter(year=alum.year, school=alum_school)
    else:
        alum_list = []

    school_list = School.objects.filter(approved=True) \
        .exclude(alumni__user=profile)

    bit = request.session.get('school_search') or ''
    school_list = school_list.filter(Q(name__icontains=bit)
                                     | Q(city__icontains=bit)
                                     | Q(state__icontains=bit)
                                     | Q(country__icontains=bit))

    school_list = school_list.annotate(num_al=Count('alumni')) \
                .order_by('-num_al')

    paginator = Paginator(school_list, SCHOOLS_PER_PAGE)

    page = request.GET.get('page')
    try:
        schools = paginator.page(page)
    except PageNotAnInteger:
        schools = paginator.page(1)
    except EmptyPage:
        schools = paginator.page(paginator.num_pages)

    return render(request, 'schools/schools.html',
                  {'school_list': schools,
                  'alum_schools': alum_schools,
                  'alum_list': alum_list})


def detail(request):
    if request.user.is_authenticated() and request.is_ajax() \
            and request.method == 'POST':
        school_id = request.POST['school_id']
        school_year = request.POST['school_year']
        school = School.objects.get(id=school_id)
        alum_list = Alum.objects.filter(year=school_year, school=school)
        alum_school_in_year = alum_list.count()

        context = {'user': request.user,
                   'school': school,
                   'alum_year': school_year,
                   'alum_list': alum_list,
                   'alum_school_in_year': alum_school_in_year}
        detail_html = render_to_string('schools/_school_detail.html', context)

        data = {'status': 'OK', 'school': detail_html}

        return HttpResponse(json.dumps(data), "application/json")
    raise Http404


def add(request):
    if request.user.is_authenticated() and request.is_ajax() \
            and request.method == 'POST':
        data = {'status': 'OK'}

        name = request.POST.get('name')
        website = request.POST.get('website')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')

        school = School(name=name, website=website, city=city, state=state,
                        country=country, user_proposed=request.user)
        school.save()

        return HttpResponse(json.dumps(data), "application/json")
    raise Http404


def join(request):
    if request.user.is_authenticated() and request.is_ajax() \
            and request.method == 'POST':
        data = {'status': 'OK'}
        year = request.POST['year']
        school_id = request.POST['school_id']

        profile = UserProfile.objects.get(id=request.user.id)
        if School.objects.filter(id=school_id, alumni__user=profile):
            data['status'] = 'faile'
            return HttpResponse(json.dumps(data))

        alum = Alum(user=profile, year=year)
        alum.save()

        school = School.objects.get(id=school_id)
        school.alumni.add(alum)

        alum_school_html = render_to_string('schools/_alum_school.html',
                                            {'school': school,
                                             'year': year}
                                            )
        data['alum_school'] = alum_school_html
        data['school_id'] = school.id

        return HttpResponse(json.dumps(data), "application/json")
    raise Http404


def leave(request):
    if request.user.is_authenticated() and request.is_ajax() \
            and request.method == 'POST':
        data = {'status': 'OK'}

        profile = UserProfile.objects.get(id=request.user.id)

        school_id = request.POST['school_id']
        school_year = request.POST['school_year']
        school = School.objects.get(id=school_id)

        alum = Alum.objects.get(user=profile, year=school_year, school=school)
        if alum:
            school.alumni.remove(alum)
            alum.delete()

        school_list = School.objects.filter(approved=True) \
            .exclude(alumni__user=profile)

        find_school_html = render_to_string('schools/_school_find.html',
                                            {'school_list': school_list},
                                            context_instance=RequestContext(request))
        data['find_school'] = find_school_html

        return HttpResponse(json.dumps(data), "application/json")


def search(request):
    if request.user.is_authenticated() and request.is_ajax() \
            and request.method == 'GET':
        data = {'status': 'OK'}

        bit = request.GET['search']
        request.session['school_search'] = bit

        profile = UserProfile.objects.get(id=request.user.id)

        school_list = School.objects.filter(approved=True) \
            .exclude(alumni__user=profile)

        school_list = school_list.filter(Q(name__icontains=bit)
                                            | Q(city__icontains=bit)
                                            | Q(state__icontains=bit)
                                            | Q(country__icontains=bit))
        paginator = Paginator(school_list, SCHOOLS_PER_PAGE)

        page = request.GET.get('page')

        try:
            schools = paginator.page(page)
        except PageNotAnInteger:
            schools = paginator.page(1)
        except EmptyPage:
            schools = paginator.page(paginator.num_pages)

        context = {'school_list': schools}
        schools_html = render_to_string('schools/_school_list.html', context)

        data['school_list'] = schools_html
        data['school_search_placeholder'] = 'Searching... {0}'.format(bit) if \
            bit else 'Search by Name or Location'

        return HttpResponse(json.dumps(data), "application/json")


def alum_in_year(request):
    if request.user.is_authenticated() and request.is_ajax() \
            and request.method == 'GET':
        data = {'status': 'OK'}

        year = request.GET['school_year']
        school_id = request.GET['school_id']
        school = School.objects.get(id=school_id)

        alumni = Alum.objects.filter(year=year, school=school)
        alum_school_in_year = alumni.count()

        results_html = render_to_string('schools/_alum_school_in_year.html',
                                        {'alum_school_in_year': alum_school_in_year})
        data['results'] = results_html

        return HttpResponse(json.dumps(data), "application/json")
