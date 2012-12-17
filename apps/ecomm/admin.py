from django.contrib import admin
from .models import Summary

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'page', 'amount', 'currency', 'date', 'type')
    list_filter = ['date','type']
    date_hierarchy = 'date'
    readonly_fields = ('user', 'page', 'amount', 'currency', 'date', 'type')

admin.site.register(Summary, SummaryAdmin)


