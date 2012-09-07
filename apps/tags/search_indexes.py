import datetime
from haystack.indexes import *
from haystack import site
from .models import Tag

class TagIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    name = CharField(model_attr='name')
    
site.register(Tag, TagIndex)

