from django import forms
from .models import *

BUSINESS_CATEGORY = (
    ('Undefined', 'Undefined'),
    ('Accomodation', 'Accomodation'),
    ('Airline', 'Airline'),
    ('Automotive', 'Automotive'),
    ('Automotive (Dealer)', 'Automotive (Dealer)'),
    ('Automotive (Service)', 'Automotive (Service)'),
    ('Bank', 'Bank'),
    ('Bar/Pub ', 'Bar/Pub '),
    ('Bar/Club', 'Bar/Club'),
    ('Computer (Software)', 'Computer (Software)'),
    ('Computer/Gadget (Hardware)', 'Computer/Gadget (Hardware)'),
    ('Consultant', 'Consultant'),
    ('Convenience Store', 'Convenience Store'),
    ('Energy', 'Energy'),
    ('Entertainment (Cinema)', 'Entertainment (Cinema)'),
    ('Entertainment (Performance)', 'Entertainment (Performance)'),
    ('Fashion (Brand)', 'Fashion (Brand)'),
    ('Fashion (Cosmetic Brand)', 'Fashion (Cosmetic Brand)'),
    ('Fashion (Footwear Brand)', 'Fashion (Footwear Brand)'),
    ('Food/Drink (Brand/Supplier)', 'Food/Drink (Brand/Supplier)'),
    ('Food/Drink (Cafe)', 'Food/Drink (Cafe)'),
    ('Food/Drink (Counter Served)', 'Food/Drink (Counter Served)'),
    ('Food/Drink (Drive Thru)', 'Food/Drink (Drive Thru)'),
    ('Food/Drink (Waitstaff Served)', 'Food/Drink (Waitstaff Served)'),
    ('Groceries', 'Groceries'),
    ('Industrial', 'Industrial'),
    ('Insurance', 'Insurance'),
    ('Health (Treatment)', 'Health (Treatment)'),
    ('Health (Gym/Studio)', 'Health (Gym/Studio)'),
    ('Media', 'Media'),
    ('Media (Internet)', 'Media (Internet)'),
    ('Media (Print)', 'Media (Print)'),
    ('Media (Social)', 'Media (Social)'),
    ('Media (TV/Movie)', 'Media (TV/Movie)'),
    ('Phone/Internet Provider', 'Phone/Internet Provider'),
    ('Recreation', 'Recreation'),
    ('Recreation (Theme/Water Park)', 'Recreation (Theme/Water Park)'),
    ('Resort/Spa', 'Resort/Spa'),
    ('Retail', 'Retail'),
    ('Retail (Art)', 'Retail (Art)'),
    ('Retail (Clothing)', 'Retail (Clothing)'),
    ('Retail (Electronics)', 'Retail (Electronics)'),
    ('Retail (Footwear)', 'Retail (Footwear)'),
    ('Retail (Home Improvement)', 'Retail (Home Improvement)'),
    ('Retail (Office)', 'Retail (Office)'),
    ('Retail (Pet)', 'Retail (Pet)'),
    ('Retail (Specialty)', 'Retail (Specialty)'),
    ('Retail (Sports/Recreation)', 'Retail (Sports/Recreation)'),
    ('Services', 'Services'),
    ('Services (Accounting)', 'Services (Accounting)'),
    ('Services (Legal)', 'Services (Legal)'),
    ('Services (Web)', 'Services (Web)'),
    ('Travel', 'Travel'),
)

NONPROFIT_CATEGORY = (
    ('Undefined', 'Undefined'),
    ('Advocacy', 'Advocacy'),
    ('Advocacy (Policy)', 'Advocacy (Policy)'),
    ('Animals', 'Animals'),
    ('Art/Culture', 'Art/Culture'),
    ('Art/Culture (Music)', 'Art/Culture (Music)'),
    ('Art/Culture (Theater)', 'Art/Culture (Theater)'),
    ('Business', 'Business'),
    ('Business (Grants/Micro-Loans)', 'Business (Grants/Micro-Loans)'),
    ('Disaster Response/Relief', 'Disaster Response/Relief'),
    ('Counseling/Intervention', 'Counseling/Intervention'),
    ('Counseling/Intervention (Domestic Abuse)', 'Counseling/Intervention (Domestic Abuse)'),
    ('Counseling/Intervention (Drugs)', 'Counseling/Intervention (Drugs)'),
    ('Education', 'Education'),
    ('Education (Family/Health)', 'Education (Family/Health)'),
    ('Education (Literacy)', 'Education (Literacy)'),
    ('Education (Nature)', 'Education (Nature)'),
    ('Education (Technology)', 'Education (Technology)'),
    ('Environment', 'Environment'),
    ('Environment (Forests)', 'Environment (Forests)'),
    ('Environment (Oceans)', 'Environment (Oceans)'),
    ('Environment (Protection)', 'Environment (Protection)'),
    ('Environment (Reduce, Reuse, Recycle)', 'Environment (Reduce, Reuse, Recycle)'),
    ('Environment (Restoration)', 'Environment (Restoration)'),
    ('Equality', 'Equality'),
    ('Food Bank/Soup Kitchen', 'Food Bank/Soup Kitchen'),
    ('Funds/Foundations', 'Funds/Foundations'),
    ('Health', 'Health'),
    ('Housing', 'Housing'),
    ('Human Rights', 'Human Rights'),
    ('Human Rights (Trafficking)', 'Human Rights (Trafficking)'),
    ('Human Services', 'Human Services'),
    ('Outreach', 'Outreach'),
    ('Outreach (Youth)', 'Outreach (Youth)'),
    ('People with Disabilities', 'People with Disabilities'),
    ('Poverty Relief', 'Poverty Relief'),
    ('Refugee/Immigrant Support', 'Refugee/Immigrant Support'),
    ('Science/Technology', 'Science/Technology'),
    ('Social Justice', 'Social Justice'),
)


class PageForm(forms.ModelForm):
    represent = forms.BooleanField(label='I have the legal right to represent this business entity.', required=True)
    terms =  forms.BooleanField(label='I agree to the terms.',
            required=True,
            widget=forms.CheckboxInput(attrs = {'style':'margin-left: 20px;'}))

    class Meta:
        model = Pages
        fields = ('name','username','category','type')

    def clean_username(self):
        data = self.cleaned_data['username']
        if '-' in data:
            raise forms.ValidationError('Sorry, you can\'t use \'-\'')
        return data


class BusinessForm(PageForm):
    class Meta:
        model = Pages
        fields = ('name','username','category','type')
        widgets = {
                'category': forms.Select(choices=BUSINESS_CATEGORY),
        }


class NonprofitForm(PageForm):
    class Meta:
        model = Pages
        fields = ('name','username','category','type')
        widgets = {
                'category': forms.Select(choices=NONPROFIT_CATEGORY),
        }


class ImageUploadForm(forms.ModelForm):

    class Meta:
        model = Pages
        fields = ('cover_photo',)

    def clean_cover_photo(self):
        try:
            image = self.cleaned_data['cover_photo']
        except KeyError:
            raise forms.ValidationError("Couldn't read uploaded image")
        if image.content_type == 'image/gif':
            raise forms.ValidationError("Sorry! Gif is prohibited.")
        if image._size > 3*1024*1024:
            raise forms.ValidationError("Image file too large ( > 3mb )")
        return image

class PageSettingsForm(forms.ModelForm):

    class Meta:
        model = Pages
        exclude = ('type','user','loves')
        widgets = {
            'username' : forms.TextInput(attrs={'readonly':'readonly'}),
        }


    def __init__(self, *args, **kwargs):
        super(PageSettingsForm, self).__init__(*args, **kwargs)
        # if we are using model in form
        if 'instance' in kwargs:
            # use appropriate catogory
            if kwargs['instance'].type == 'BS':
                self.fields['category'].widget = forms.Select(choices=BUSINESS_CATEGORY)
            else:
                self.fields['category'].widget = forms.Select(choices=NONPROFIT_CATEGORY)



