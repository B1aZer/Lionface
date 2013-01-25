# Create your views here.
from django.views.generic import TemplateView

from socketio import socketio_manage
from .chat_socketio import ChatNamespace

class HomeView(TemplateView):
    template_name = 'chat/chat.html'

