from django.core.mail import send_mail
from celery import shared_task
from .models import Email
from django.contrib.auth.models import User

@shared_task(bind=True, max_retries=3)
def send_email_task(self, recipient, subject, body, user_id):
    try:
        user = User.objects.get(id=user_id)

        send_mail(
            subject,
            body,
            user.email,
            [recipient],
        )
        
        Email.objects.create(
            recipient=recipient,
            subject=subject,
            body=body,
            user=user
        )
    except Exception as exc:
        raise self.retry(exc=exc, coundown=60)
    

    