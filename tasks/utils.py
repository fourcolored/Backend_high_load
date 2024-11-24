from .models import OTP
from django.core.mail import send_mail
from django.conf import settings

def send_2fa_otp(user):
    otp, _ = OTP.objects.get_or_create(user=user)
    
    otp_code = otp.generate_otp()

    send_mail(
        "Your 2FA Code",
        f"Your 2FA code is {otp_code}.",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

    return otp_code
