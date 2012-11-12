import datetime
from haystack.indexes import *
from haystack import site
from .models import Pages

class PageIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    page_type = CharField(model_attr='type') 
    username = CharField(model_attr='username')
    username_auto = EdgeNgramField(model_attr='username')
    full_name = CharField(model_attr='name')
    full_name_auto = EdgeNgramField(model_attr='name')

site.register(Pages, PageIndex)
