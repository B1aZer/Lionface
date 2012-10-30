import datetime
from django import template
from django.template.loader import render_to_string
from account.forms import LoginForm

register = template.Library()

@register.simple_tag(takes_context=True)
def header(context, user=None):
    if user.is_anonymous():
        login_form = LoginForm(prefix='login')
        return render_to_string('public/_login_box.html',
                {
                    'login_form':login_form,
                },
                context)
    else:
        return render_to_string('_header.html', context)
