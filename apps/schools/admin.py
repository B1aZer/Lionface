from django.contrib import admin
from .models import School


class SchoolAdmin(admin.ModelAdmin):
    fields = ['name', 'website', 'city', 'state', 'country', 'approved']
    list_display = ('name', 'user_proposed_school', 'approved')
    list_filter = ['approved']

    def user_proposed_school(self, obj):
        return '<a href="{0}">{1}</a>' \
            .format(obj.user_proposed.get_absolute_url(),
                    obj.user_proposed.get_full_name())
    user_proposed_school.allow_tags = True

admin.site.register(School, SchoolAdmin)