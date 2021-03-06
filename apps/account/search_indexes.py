import datetime
from haystack.indexes import *
from haystack import site
from django.contrib.auth.models import User
from .models import UserProfile

class UserIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    username = CharField(model_attr='username')
    email = CharField(model_attr='email')
    username_auto = EdgeNgramField(model_attr='username')
    first_auto = EdgeNgramField(model_attr='first_name')
    last_auto = EdgeNgramField(model_attr='last_name')
    full_name = CharField(model_attr='optional_name')
    full_name_auto = EdgeNgramField(model_attr='optional_name')

site.register(UserProfile, UserIndex)
