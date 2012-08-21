from django import forms
from account.models import *

class ImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('photo',)
    
     # Add some custom validation to our image field
    def clean_image(self):
         image = self.cleaned_data.get('image',False)
         if image:
             if image._size > 1*1024*1024:
                   raise forms.ValidationError("Image file too large ( > 1mb )")
             return image
         else:
             raise forms.ValidationError("Couldn't read uploaded image")


