from django import forms
from .models import *

class MessageForm(forms.Form):
    user_to = forms.CharField(max_length=100, required = False, widget=forms.TextInput(attrs={'style':'width: 300px !important; padding: 7px; -moz-border-radius: 3px; border-radius: 3px; border: 1px solid #DDD;'}))
    user_id = forms.IntegerField(required = False, widget=forms.HiddenInput)
    content = forms.CharField(max_length=1000, required = True, widget=forms.Textarea(attrs={'style':'width: 100% !important; min-height: 100px !important; -moz-border-radius: 3px; border-radius: 3px; border: 1px solid #DDD; line-height: 1;','cols':'40'}))

    def clean(self):
        data = self.cleaned_data
        if not data.get('user_id',None):
            raise forms.ValidationError("Wrong recipient.")
        return data

