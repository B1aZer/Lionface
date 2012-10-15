from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response

@login_required
def main(request, username=None):

    return render_to_response(
        'pages/main.html',
        {
        },
        RequestContext(request)
    )

@login_required
def page(request, username=None):

    return render_to_response(
        'pages/page.html',
        {
        },
        RequestContext(request)
    )
