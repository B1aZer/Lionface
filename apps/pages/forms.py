from django import forms
from .models import *

class PageForm(forms.ModelForm):

    class Meta:
        model = Pages
        fields = ('name','username','category',)
