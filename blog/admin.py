from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_date', 'get_tags')

    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])
    

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'content', 'created_date')


# Register your models here.
admin.site.register(Tag)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User, UserAdmin)

