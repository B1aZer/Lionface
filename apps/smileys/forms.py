from django import forms

class Uploading(forms.Form):
    import_file = forms.FileField()
