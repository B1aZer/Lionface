from django.db import models
from django.db.models.fields.files import ImageFieldFile

from .utils import get_thumb_name


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


class CoordsField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None:
            return
        try:
            if isinstance(value, basestring):
                value = json.loads(value)
        except ValueError:
            pass
        return value

    def get_db_prep_save(self, value):
        if value is None:
            return
        value = json.dumps(value)
        return super(CoordsField, self).get_db_prep_save(value)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^account\.fields\.CoordsField"])
    add_introspection_rules([], ["^account\.fields\.ImageWithThumbField"])
except:
    pass
