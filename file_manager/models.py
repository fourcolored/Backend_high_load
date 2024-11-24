from django.db import models
from django.contrib.auth.models import User

class FileModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
        ]
        permissions = [
            ('can_add_file', 'Can add file model'),
            ('can_view_file', 'Can view file model'),
        ]

    def __str__(self) -> str:
        return self.file.name