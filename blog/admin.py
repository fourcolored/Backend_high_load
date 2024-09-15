from django.contrib import admin

# Register your models here.
from .models import Post, Comment

# class Post(admin.ModelAdmin):
#     pass

# password: admin; email: admin@mail.ru; username: admin

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at']
    search_fields = ['title']

class CommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Comment._meta.get_fields()]

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)