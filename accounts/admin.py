from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import WorkerProfile


class WorkerProfileInlineAdmin(admin.StackedInline):
    model = WorkerProfile
    can_delete = False
    verbose_name_plural = 'Профіль виконавця'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (WorkerProfileInlineAdmin, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_group')
    list_select_related = ('worker_profile',)

    def get_group(self, instance):
        return instance.groups.all().first()
    get_group.short_description = 'Група'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
