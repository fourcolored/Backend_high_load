import random
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password


from encrypted_model_fields.fields import EncryptedTextField, EncryptedEmailField

# Create your models here.

class Email(models.Model):
    user = models.ForeignKey(User, related_name='emails', on_delete=models.CASCADE)
    recipient = EncryptedEmailField() 
    subject = models.CharField(max_length=500)
    body = EncryptedTextField()

    class Meta:
        permissions = [
            ('can_view_email', 'Can view email'),
            ('can_create_email', 'Can create email'),
            ('can_delete_email', 'Can delete email'),
            ('can_send_email', 'Can send email'),
        ]

class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def generate_otp(self):
        code = f"{random.randint(100000, 999999):06}"
        self.code = make_password(code)
        self.expires_at = now() + timedelta(minutes=1)
        self.save()

        return code

    def is_valid(self, code):
        return check_password(code, self.code) and self.expires_at > now()
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    website = models.URLField()

    def __str__(self):
        return self.name