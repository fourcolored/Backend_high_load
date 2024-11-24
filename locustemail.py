from locust import HttpUser, between, task, SequentialTaskSet
import random
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

class WebsiteUser(HttpUser):
    wait_time = between(5, 15)
    host = "http://localhost:8000/"

    token = None
    csrf_token = None
    
    def on_start(self):
        user_id, otp_code = self.login()
        self.verify_otp(user_id, otp_code)
    
    def login(self):
        response = self.client.get("/login/") 

        csrf_token = response.cookies.get("csrftoken")
        if not csrf_token:
            csrf_token = response.headers.get("X-CSRFToken") 

        response = self.client.post("/login/", {
            "username": "user",
            "password": "p4ssword123"
            },
            headers={"X-CSRFToken": csrf_token},
            cookies={"csrftoken": csrf_token}
        )
        
        if response.status_code == 200:
            user_id = response.cookies.get('temp_user_id')
            otp_code = response.json().get('code')
            self.csrf_token = csrf_token
        else:
            user_id = None
            otp_code = None
            self.csrf_token = None

        return user_id, otp_code
    
    def verify_otp(self, user_id, otp_code):
        if not user_id or not otp_code or not self.csrf_token:
            return
        
        payload = {
            "code": otp_code
        }

        cookies = {
            "csrftoken": self.csrf_token,
            "temp_user_id": user_id
        }

        response = self.client.post(
            "/otp-auth/",
            json=payload,
            headers={"X-CSRFToken": self.csrf_token},
            cookies=cookies
        )

        if response.status_code == 302:
            self.token = response.cookies.get('jwt_token')
        else:
            self.token = None
    
    @task(1)
    def send_email(self):
        """
        Simulates sending email
        """
        if not self.token or not self.csrf_token:
            user_id, otp_code = self.login()
            self.verify_otp(user_id, otp_code)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-CSRFToken": self.csrf_token
        }
        cookies = {
            "csrftoken": self.csrf_token
        }
        payload = {
            "recipient": "recipient@example.com",
            "subject": "Test Email",
            "body": "This is a test email body."
        }
        self.client.post("/send-email/", json=payload, headers=headers, cookies=cookies)
    
    @task(2)
    def view_emails(self):
        """
        Simulates fetching a list of emails for the user.
        """
        if not self.token:
            user_id, otp_code = self.login()
            self.verify_otp(user_id, otp_code)

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        self.client.get("/send-email/", headers=headers)
    
    def on_stop(self):
        if not self.token or not self.csrf_token:
            return
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-CSRFToken": self.csrf_token
        }
        cookies = {
            "csrftoken": self.csrf_token
        }

        self.client.post("/logout/", headers=headers, cookies=cookies)
