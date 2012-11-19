from django.db import models
from django.db.models.fields.files import ImageFieldFile

from .storage import ImageStorage, get_thumb_name


class ImageWithThumbFieldFile(ImageFieldFile):
    """
    As ImageFieldFile, only with some propertys for thumb
    """

    def _get_thumb_name(self):
        return get_thumb_name(self.name)
    thumb_name = property(_get_thumb_name)

    def _get_thumb_path(self):
        return get_thumb_name(self.path)
    thumb_path = property(_get_thumb_path)


class ImageWithThumbField(models.ImageField):
    """
    As ImageField, only change attr_class for thumb_name and thumb_path
    """
    attr_class = ImageWithThumbFieldFile

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'storage': ImageStorage(),
        })
        super(ImageWithThumbField, self).__init__(*args, **kwargs)

    def delete(self, save=False):
        ret = super(ImageWithThumbField, self).delete(save)
        self.storage.delete(self.thumb_path)
        return ret


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^images\.fields\.ImageWithThumbField"])
except:
    pass
