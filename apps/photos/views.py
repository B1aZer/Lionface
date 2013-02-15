from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext

from images.models import *
from account.models import UserProfile
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone
import datetime

from django.db.models import Count

def home(request):
    manage_perm = False
    rows_show = 4
    now = timezone.now()
    week_ago = now - datetime.timedelta(days=7)
    #ctype = ContentType.objects.get_for_model(UserProfile)
    qs = Image.objects.filter(imageloves__date__gte=week_ago).annotate(num_loves=Count('users_loved')).order_by('-num_loves')
    #qs = ImageLoves.objects.filter(date__gte=week_ago).order_by('user')
    return render_to_response(
        'photos/home.html',
        {
            'profile_user': request.user,
            'image_rows': qs.get_rows(0, rows_show, order=False),
            'total_rows': qs.total_rows(),
            'photos_count': qs.count(),
            'manage_perm': manage_perm,
        },
        RequestContext(request)
    )

