from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.shortcuts import render

try:
    import json
except ImportError:
    import simplejson as json

from .models import School


def home(request):
    school_list = School.objects.all()
    return render(request, 'schools/schools.html',
        {
            'school_list': school_list,
        }
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

        school_html = render_to_string('schools/_school.html',
            {'school': school})
        data['school'] = school_html
        return HttpResponse(json.dumps(data), "application/json")
    raise Http404
