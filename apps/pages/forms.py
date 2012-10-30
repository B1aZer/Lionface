from django import forms
from .models import *

class PageForm(forms.ModelForm):
    represent = forms.BooleanField(label='I have the legal right to represent this business entity.', required=True)
    terms =  forms.BooleanField(label='I agree to the terms.',
            required=True,
            widget=forms.CheckboxInput(attrs = {'style':'margin-left: 20px;'}))

    class Meta:
        model = Pages
        fields = ('name','username','category','type')

