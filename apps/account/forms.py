from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
import re, datetime

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=20, min_length=4, widget=forms.PasswordInput())
    preserve = forms.BooleanField(label='Stay logged in', required=False)
    
    def login(self, request):
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
            user = authenticate(username=user.username, password=self.cleaned_data['password'])
            if user is not None:
                login(request, user)
            if self.cleaned_data['preserve']:
                request.session.set_expiry(datetime.timedelta(days=365))
            return user
        except User.DoesNotExist:
            print "No user was found with this e-mail address [%s]." % (self.cleaned_data['email'])
            return None

    
class SignupForm(forms.Form):
    full_name = forms.CharField(required=True, label="Full Name", help_text="You can change this later.")
    password = forms.CharField(max_length=20, min_length=4, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=20, min_length=4, widget=forms.PasswordInput(), label="Confirm Password")
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True, label="Username", help_text="lionface.org/username")
    terms = forms.BooleanField(label='I agree to the Terms.', required=False)
    
    def clean_full_name(self):
        if not re.search("[a-zA-Z]{2,} [a-zA-Z]{2,}", self.cleaned_data['full_name']):
            raise forms.ValidationError("Please enter your full name.")
        return self.cleaned_data['full_name']

    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Check it doesn't already exist.
        if User.objects.filter(email__iexact=email).count() > 0:
            raise forms.ValidationError("A user has already registered with this e-mail address.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        
        if not re.search("^[a-zA-Z0-9_]{1,}$", username):
            raise forms.ValidationError("Usernames can only contain letters, numbers and underscores.")
        
        # Check it doesn't already exist.
        if User.objects.filter(username__iexact=username).count() > 0:
            raise forms.ValidationError("A user has already registered with this e-mail address.")
        return username
    
    def clean(self):
        data = self.cleaned_data
        if not data['terms']:
            self._errors['terms'] = self.error_class(['You must accept the terms.'])
        
        if 'password' in data and 'password2' in data:
            if data['password'] != data['password2']:
                self._errors['password2'] = self.error_class(['Passwords do not match.'])
        return data
    
    def save(self):
        data = self.cleaned_data
        
        user = User.objects.create_user(data['username'], data['email'], data['password'])
        user.first_name = data['full_name'].split(' ', 2)[0]
        user.last_name = data['full_name'].split(' ', 2)[1]
        user.save()
        return user

