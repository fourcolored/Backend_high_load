from django.contrib import admin
from .models import Email,OTP

class EmailAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipient', 'subject','body')

class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'expires_at')

# Register your models here.
admin.site.register(Email, EmailAdmin)
admin.site.register(OTP)
