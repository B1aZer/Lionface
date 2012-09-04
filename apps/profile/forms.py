from django import forms
from account.models import *
from django.forms import TextInput

class ImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('photo',)

     # Add some custom validation to our image field
    def clean_photo(self):
         image = self.cleaned_data.get('photo',False)
         if image:
             if image._size > 1*1024*1024:
                   raise forms.ValidationError("Image file too large ( > 1mb )")
             return image
         else:
             raise forms.ValidationError("Couldn't read uploaded image")


class UserInfoForm(forms.ModelForm):
    full_name = forms.CharField(required=False, label="Full Name" , widget=forms.TextInput(attrs={'style': 'border: 1px solid #DDD; padding: 7px; width: 300px;'}))
    class Meta:
        model = UserProfile
        fields = ('full_name', 'email', 'first_name', 'last_name')
        widgets = {
            'email': TextInput(attrs={'style': 'border: 1px solid #DDD; padding: 7px; width: 300px;'}),
        }
    def __init__(self, *args, **kwargs):
        super(UserInfoForm, self).__init__(*args, **kwargs)

        # Set the form fields based on the model object
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['full_name'] = instance.full_name

    def save(self, commit=True):
        #import pdb;pdb.set_trace()
        data = self.cleaned_data

        data['username'] = self.instance.username

        user = super(UserInfoForm, self).save(commit=False)
        user.first_name = data['full_name'].split(' ', 2)[0]
        user.last_name = data['full_name'].split(' ', 2)[1]

        if commit:
            user.save()

        return user





