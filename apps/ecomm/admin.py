from django.contrib import admin
from .models import Summary

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'page', 'amount', 'currency', 'date', 'type')
    list_filter = ['date','type']
    date_hierarchy = 'date'
    readonly_fields = ('user', 'page', 'amount', 'currency', 'date', 'type')
    ordering = ['-date']
    actions = None

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['summaries'] = self.queryset(request)
        if request.GET.get('type__exact', None) == 'B':
            extra_context['bidding'] = True
        result = super(SummaryAdmin, self).changelist_view(request, extra_context)
        return result

admin.site.register(Summary, SummaryAdmin)


