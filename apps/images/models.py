from django.db import models
from django.db.models.signals import post_save, post_delete
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from PIL import Image as pilImage
from PIL import ExifTags

from account.models import UserProfile
from post.models import QuerySet as CustomQuerySet
from .fields import ImageWithThumbField

import os


class ImageQuerySet(CustomQuerySet):
    DEFAULT_ROW_SIZE = 4

    def total_rows(self, row_size=DEFAULT_ROW_SIZE):
        from math import ceil
        return int(ceil(self.count() / float(row_size)))

    def get_rows(self, start, count, row_size=DEFAULT_ROW_SIZE, order=True):
        if order:
            qs = self.order_by('rating')
        else:
            qs = self
        objs = qs[start * row_size:(start + count) * row_size]
        rows = []
        for i in xrange(0, len(objs), row_size):
            rows.append(objs[i:i + row_size])
        return rows

    def get_row(self, start, row_size=DEFAULT_ROW_SIZE):
        return self.get_rows(start, 1, row_size=row_size)[0]

    def get_positions(self):
        return dict(
            [(d['pk'], d['rating']) for d in self.values('pk', 'rating')]
        )

class ImageLoves(models.Model):
    post = models.ForeignKey('Image')
    user = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)

class Image(models.Model):
    image = ImageWithThumbField(upload_to="uploads/images")
    owner_type = models.ForeignKey(ContentType)
    owner_id = models.PositiveIntegerField()
    owner = generic.GenericForeignKey('owner_type', 'owner_id')
    rating = models.IntegerField(blank=True, null=True)
    activity = models.BooleanField(default=False)
    following = models.ManyToManyField( UserProfile, related_name='follows_images', null=True, blank=True)
    users_loved = models.ManyToManyField(
        UserProfile, related_name='images_loved', through='ImageLoves', null=True, blank=True)

    objects = ImageQuerySet.as_manager()

    def __unicode__(self):
        return self.image.name

    def get_owner(self):
        if isinstance(self.owner, UserProfile):
            return self.owner
        else:
            try:
                user = self.owner.user
                return user
            except:
                return None

    def get_loves(self):
        return self.users_loved.count()

    def get_medium_thumb(self):
        name, ext = os.path.splitext(self.image.thumb_name)
        name = name + '_med' + ext
        if os.path.exists(name):
            return name
        else:
            return self.image.thumb_name

    def get_large_thumb(self):
        name, ext = os.path.splitext(self.image.thumb_name)
        name = name + '_lrg' + ext
        if os.path.exists(name):
            return name
        else:
            return self.image.thumb_name

    def change_position(self, old, new, save=True, selflock=None):
        if old == new:
            return False
        if selflock is None:
            selflock = self.__class__.objects \
                .filter(pk=self.pk) \
                .select_for_update() \
                .get()
        qs = self.__class__.objects \
            .filter(owner_type=self.owner_type, owner_id=self.owner_id)
        if old > new:
            qs.filter(rating__gte=new, rating__lte=old) \
                .update(rating=models.F('rating') + 1)
        elif new > old:
            qs.filter(rating__gte=old, rating__lte=new) \
                .update(rating=models.F('rating') - 1)
        selflock.rating = new
        if save:
            selflock.save()
        return selflock

    def make_activity(self):
        min_rating = self.__class__.objects \
            .filter(owner_type=self.owner_type, owner_id=self.owner_id) \
            .aggregate(models.Min('rating')) \
            .get('rating__min')
        if min_rating is None:
            return False
        if min_rating != self.rating:
            selflock = self.change_position(self.rating, min_rating, save=False)
        else:
            selflock = self.__class__.objects \
                .filter(pk=self.pk) \
                .select_for_update() \
                .get()
        self.__class__.objects \
            .filter(owner_type=self.owner_type, owner_id=self.owner_id) \
            .filter(activity=True) \
            .update(activity=False)
        selflock.activity = True
        selflock.save()
        self.owner.photo = self.image
        self.owner.save()
        return True

    def change_orientation(self, angle=False):
        pil_object = pilImage.open(self.image.path)
        # reading and applying orientation
        for orientation in ExifTags.TAGS.keys() :
            if ExifTags.TAGS[orientation]=='Orientation' : break
        try:
            exif=dict(pil_object._getexif().items())
            if   exif[orientation] == 3 :
                pil_object=pil_object.rotate(180, expand=True)
            elif exif[orientation] == 6 :
                pil_object=pil_object.rotate(270, expand=True)
            elif exif[orientation] == 8 :
                pil_object=pil_object.rotate(90, expand=True)
        except:
            pass
        if angle:
            pil_object=pil_object.rotate(angle, expand=False)
        pil_object.save(self.image.path)
        return True

    def change_thumb_orientation(self, angle=False, size=None):
        if not size:
            pil_object = pilImage.open(self.image.thumb_path)
        elif size == 'medium':
            name, ext = os.path.splitext(self.image.thumb_path)
            name = name + '_med' + ext
            pil_object = pilImage.open(name)
        elif size == 'large':
            name, ext = os.path.splitext(self.image.thumb_path)
            name = name + '_lrg' + ext
            pil_object = pilImage.open(name)
        # reading and applying orientation
        for orientation in ExifTags.TAGS.keys() :
            if ExifTags.TAGS[orientation]=='Orientation' : break
        try:
            exif=dict(pil_object._getexif().items())
            if   exif[orientation] == 3 :
                pil_object=pil_object.rotate(180, expand=True)
            elif exif[orientation] == 6 :
                pil_object=pil_object.rotate(270, expand=True)
            elif exif[orientation] == 8 :
                pil_object=pil_object.rotate(90, expand=True)
        except:
            pass
        if angle:
            pil_object=pil_object.rotate(angle, expand=False)
        if not size:
            pil_object.save(self.image.thumb_path)
        elif size == 'medium':
            pil_object.save(name)
        elif size == 'large':
            pil_object.save(name)
        return True

    def generate_thumbnail(self, width, height, quiet=True, angle=None, size=None):
        try:
            pil_object = pilImage.open(self.image.path)
            # reading and applying orientation
            for orientation in ExifTags.TAGS.keys() :
                if ExifTags.TAGS[orientation]=='Orientation' : break
            try:
                exif=dict(pil_object._getexif().items())
                if   exif[orientation] == 3 :
                    pil_object=pil_object.rotate(180, expand=True)
                elif exif[orientation] == 6 :
                    pil_object=pil_object.rotate(270, expand=True)
                elif exif[orientation] == 8 :
                    pil_object=pil_object.rotate(90, expand=True)
            except:
                pass
            if angle:
                pil_object=pil_object.rotate(angle, expand=False)

            w, h = pil_object.size
            x, y = 0, 0
            if w > h:
                x, y, w, h = int((w - h) / 2), 0, h, h
            elif h > w:
                x, y, w, h = 0, int((h - w) / 2), w, w
            new_pil_object = pil_object \
                .crop((x, y, x + w, y + h)) \
                .resize((width, height), pilImage.ANTIALIAS)
            if not size:
                new_pil_object.save(self.image.thumb_path)
            elif size == 'medium':
                name, ext = os.path.splitext(self.image.thumb_path)
                name = name + '_med' + ext
                new_pil_object.save(name)
            elif size == 'large':
                name, ext = os.path.splitext(self.image.thumb_path)
                name = name + '_lrg' + ext
                new_pil_object.save(name)
        except:
            if not quiet:
                raise


def create_image(sender, instance, created, **kwargs):
    if created:
        instance.rating = instance.pk
        instance.following.add(instance.get_owner())
        instance.save()
post_save.connect(
    create_image,
    sender=Image,
    dispatch_uid='apps.images.signals.create_image'
)


def delete_image(sender, instance, **kwargs):
    if instance.activity:
        owner = instance.owner
        owner.photo = owner.photo.field.default
        owner.save()
    instance.following.clear()
    instance.image.storage.delete(instance.image.thumb_path)
    instance.image.delete(save=False)
post_delete.connect(
    delete_image,
    sender=Image,
    dispatch_uid='apps.images.signals.delete_image'
)


class ImageCounter(models.Model):
    owner_type = models.ForeignKey(ContentType)
    owner_id = models.PositiveIntegerField()
    owner = generic.GenericForeignKey('owner_type', 'owner_id')
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = (('owner_type', 'owner_id'),)
        db_table = 'images_counter'


class ImageComments(models.Model):
    image = models.ForeignKey('Image', related_name='comments')
    owner = models.ForeignKey(UserProfile)
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    class Meta:
        ordering = ['date']
        db_table = 'images_comments'


"""
def add_image_to_followings(sender, instance, created, **kwargs):
    if created:
        instance.image.following.add(instance.owner)
post_save.connect(add_image_to_followings, sender=ImageComments)
"""
