import os

from django import forms
from django.contrib.contenttypes.models import ContentType

from account.models import UserProfile
from pages.models import Pages
from post.models import *
from .models import Image, ImageCounter


class ImageForm(forms.Form):
    image = forms.ImageField(label='Image', required=True)

    def clean_photo(self):
        image = self.cleaned_data['image']
        if image == self.fields['image'].initial:
            raise forms.ValidationError("Please select file and send it")
        if image.content_type == 'image/gif':
            raise forms.ValidationError("Sorry! Gif is prohibited.")
        if image._size > 1 * 1024 * 1024:
            raise forms.ValidationError("Image file too large ( > 1mb )")
        return image

    def save(self, owner):
        post = None
        if isinstance(owner, ContentPost) or isinstance(owner, PagePost):
            post = owner
            owner = owner.get_owner()
        ctype = ContentType.objects.get_for_model(owner.__class__)
        try:
            counter = ImageCounter.objects \
                .select_for_update() \
                .get(owner_type=ctype, owner_id=owner.id)
        except ImageCounter.DoesNotExist:
            ImageCounter.objects.create(owner=owner)
            counter = ImageCounter.objects \
                .select_for_update() \
                .get(owner_type=ctype, owner_id=owner.id)
        counter.count += 1
        number = counter.count
        counter.save()
        if isinstance(owner, UserProfile):
            name = owner.username
            if post:
                name += '_p'
        elif isinstance(owner, Pages):
            name = owner.username
            if owner.type == 'BS':
                name += '_b'
            elif owner.type == 'NP':
                name += '_n'
            else:
                name += '_unknown'
        else:
            name = 'unknown'
        self.cleaned_data['image'].name = '%s_%d%s' % (
            name,
            number,
            os.path.splitext(self.cleaned_data['image'].name)[1],
        )
        if post:
            owner = post
        image = Image.objects.create(
            image=self.cleaned_data['image'],
            owner=owner
        )
        image.save()
        return image
