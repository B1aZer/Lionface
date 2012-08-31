# Create your views here.
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response

@login_required
def main(request):

    return render_to_response(
        'messages/main.html',
        {
        },
        RequestContext(request)
    )  
