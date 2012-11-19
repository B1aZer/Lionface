from django.db.models.signals import post_save, post_delete

from .models import Image


def create_image(sender, instance, created, **kwargs):
    if created:
        instance.rating = instance.pk
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
post_delete.connect(
    delete_image,
    sender=Image,
    dispatch_uid='apps.images.signals.delete_image'
)
