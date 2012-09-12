import datetime
from haystack.indexes import *
from haystack import site
from django.contrib.auth.models import User

class UserIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    username = CharField(model_attr='username')
    email = CharField(model_attr='email')
    username_auto = EdgeNgramField(model_attr='username')
    first_auto = EdgeNgramField(model_attr='first_name')
    last_auto = EdgeNgramField(model_attr='last_name')

site.register(User, UserIndex)
