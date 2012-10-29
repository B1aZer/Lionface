from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from .forms import *

@login_required
def main(request, username=None):

    form = PageForm()

    return render_to_response(
        'pages/business.html',
        {
            'form': form,
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

@login_required
def leaderboard(request, username=None):

    return render_to_response(
        'pages/leaderboard.html',
        {
        },
        RequestContext(request)
    )

@login_required
def nonprofit(request, username=None):

    return render_to_response(
        'pages/nonprofit.html',
        {
        },
        RequestContext(request)
    ) 
