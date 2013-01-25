from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.shortcuts import render

try:
    import json
except ImportError:
    import simplejson as json

from account.models import UserProfile
from .models import Alum, School


def home(request):
    profile = UserProfile.objects.get(id=request.user.id)
    school_list = School.objects.filter(approved=True) \
        .exclude(alumni__user=profile)
    alum_schools = School.objects.filter(approved=True, alumni__user=profile)
    alum_list = Alum.objects.all().exclude(user=profile)
    return render(request, 'schools/schools.html',
                  {'school_list': school_list,
                  'alum_schools': alum_schools,
                  'alum_list': alum_list}
    )


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

        # school_html = render_to_string('schools/_school.html',
            # {'school': school})
        # data['school'] = school_html
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
            {'school': school}
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

        return HttpResponse(json.dumps(data), "application/json")
