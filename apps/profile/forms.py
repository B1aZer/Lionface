from django import forms
from account.models import *
from django.forms import TextInput
import re

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

POSTING_DEFAULT = [('Public','Public'), ('Friends Only','Friends Only'),]
SHARE_DEFAULT = [('Enabled','Enabled'), ('Disabled','Disabled'),]
FOLLOWER_LIST = [('Public','Public'), ("Friend's Friends","Friend's Friends"), ('Friends','Friends'), ("Just Me","Just Me"),]
FOLLOW = [('Public','Public'), ("Friend's Friends","Friend's Friends"), ("Off","Off"),]
COMMENT_DEFAULT = [('Enabled','Enabled'), ('Disabled','Disabled'),]
ADD_FRIEND = [('Public','Public'), ("Friend's Friends","Friend's Friends"), ("Off","Off"),]
SEARCH = [('Public','Public'), ("Friend's Friends","Friend's Friends"), ('Friends','Friends'),]
SEND_MESSAGE = [('Public','Public'), ("Friend's Friends","Friend's Friends"), ('Friends','Friends'), ("Off","Off"),]
FRIEND_LIST = [('Public','Public'), ("Friend's Friends","Friend's Friends"), ('Friends','Friends'), ("Just Me","Just Me"),]
FOLLOWING_LIST = [('Public','Public'), ("Friend's Friends","Friend's Friends"), ('Friends','Friends'), ("Just Me","Just Me"),]

class UserInfoForm(forms.ModelForm):
    full_name = forms.CharField(required=False, label="Full Name" , widget=forms.TextInput(attrs={'style': 'border: 1px solid #DDD; padding: 7px; width: 300px;'}))

    option_posting_default = forms.ChoiceField(required=False, choices=( POSTING_DEFAULT ))
    option_share_default = forms.ChoiceField(required=False, choices=( SHARE_DEFAULT ))
    option_follower_list = forms.ChoiceField(required=False, choices=( FOLLOWER_LIST ))
    option_follow = forms.ChoiceField(required=False, choices=( FOLLOW ))
    option_comment_default = forms.ChoiceField(required=False, choices=( COMMENT_DEFAULT ))
    option_add_friend = forms.ChoiceField(required=False, choices=( ADD_FRIEND ))
    option_search = forms.ChoiceField(required=False, choices=( SEARCH ))
    option_send_message = forms.ChoiceField(required=False, choices=( SEND_MESSAGE ))
    option_friend_list = forms.ChoiceField(required=False, choices=( FRIEND_LIST ))
    option_following_list = forms.ChoiceField(required=False, choices=( FOLLOWING_LIST ))

    class Meta:
        model = UserProfile
        fields = ('full_name', 'email', 'first_name', 'last_name', 'username')
        widgets = {
            'email' : TextInput(attrs={'style': 'border: 1px solid #DDD; padding: 7px; width: 300px;'}),
            'username' : TextInput(attrs={'readonly':'readonly'}),
        }
    def __init__(self, *args, **kwargs):
        super(UserInfoForm, self).__init__(*args, **kwargs)

        # Set the form fields based on the model object
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['full_name'] = instance.full_name

    def clean_full_name(self):
        def titlecase(s):
                return re.sub("[A-Za-z]+('[A-Za-z]+)?",
                              lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:],
                              s)
        if not re.search("[a-zA-Z]{2,} [a-zA-Z]{2,}", self.cleaned_data['full_name']):
            raise forms.ValidationError("Please enter your full name.")
        if self.cleaned_data['full_name'].isupper():
            raise forms.ValidationError("Please enter your full name without caps.")
        self.cleaned_data['full_name'] = titlecase(self.cleaned_data['full_name'].strip())

        return self.cleaned_data['full_name']

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





