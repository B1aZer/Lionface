from django.contrib import admin
from .models import Pages

class PagesAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'user', 'loves_limit', 'featured', 'exempt')
    fields = ['name', 'loves_limit', 'exempt']
    search_fields = ['name', 'username']
    actions = None
    list_editable = ['exempt']

admin.site.register(Pages, PagesAdmin)


