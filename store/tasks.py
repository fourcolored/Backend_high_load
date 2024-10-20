from celery import shared_task
from .models import Order
from django.core.mail import send_mail

@shared_task
def send_purchase_result(order_id):
    try:
        order = Order.objects.get(id=order_id)
        mail_subject = f"Hi, {order.user.username}"
        message = f'The purchase was done with order id {order_id} and total sum is {order.total_price}'
        to_email = order.user.email
        send_mail(
            subject=mail_subject,
            message=message,
            recipient_list=[to_email],
            from_email="admin@ecommerce.com"
        )
    except order.DoesNotExist:
        print(f"Order with ID {order_id} does not exist.")
    except Exception as e:
        print(f"Error sending email: {e}")
    return "Done"
