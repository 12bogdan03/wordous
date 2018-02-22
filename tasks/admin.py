from django.contrib import admin

from .models import Task, Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'creator', 'task', 'created')
    list_filter = ('created',)
    search_fields = ('creator__username', 'text')


class TaskAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'kind', 'status', 'creator', 'executor',
                    'created', 'deadline', 'estimated_price')
    list_filter = ('kind', 'status', 'created', 'deadline',
                   'estimated_price')
    search_fields = ('creator__username', 'executor__username', 'description')


admin.site.register(Comment, CommentAdmin)
admin.site.register(Task, TaskAdmin)
