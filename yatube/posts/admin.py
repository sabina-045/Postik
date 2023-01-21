from django.contrib import admin

from .models import Post, Group, Comment, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настроить интерфейс администратора"""
    list_display = ('pk', 'text', 'created', 'author', 'group', )
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Follow)
