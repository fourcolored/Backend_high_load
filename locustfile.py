from locust import HttpUser, TaskSet, task
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

class FileUploadTaskSet(TaskSet):

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
    
    @task
    def upload_file(self):
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
        filename = "annual-enterprise-survey-2023-financial-year-provisional-size-bands.csv"
        with open(filename, "rb") as file:
            files = {
                'file': (filename, file, 'text/csv'),
            }
            self.client.post("/file/upload_file/", files=files, headers=headers, cookies=cookies)

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

class FileUploadUser(HttpUser):
    host = "http://localhost:8000"
    tasks = [FileUploadTaskSet]
    min_wait = 1000
    max_wait = 3000
