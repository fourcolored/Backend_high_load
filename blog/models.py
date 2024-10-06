from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField()
    email = models.CharField()
    password = models.CharField()
    Bio = models.TextField()

    def __str__(self) -> str:
        return f"{self.username}_{self.email}"
    
class Post(models.Model):
    title = models.CharField()
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField()
    tags = models.ManyToManyField()

    class Meta:
        indexes = [
            models.Index(fields=['author', 'tags'])
        ]

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User)
    content = models.TextField()
    created_date = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['post', 'created_date'])
        ]
