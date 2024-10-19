import threading
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
import datetime
from django.core.mail import send_mail
from django.core.mail import EmailMessage


# Send Forgot Password Link Via Email
class SentOTPViaEmailThread(threading.Thread):
    def __init__(self, record_data):
        self.record_data = record_data
        threading.Thread.__init__(self)

    def run(self) -> None:
        requested_email = self.record_data['email']
        print(requested_email)
        name = self.record_data['email']
        otp = self.record_data['otp']
        msg_plain = 'Grassroot Marketplace'
        subject = 'Otp for email verification'
        from_email = settings.EMAIL_HOST_USER
        email_to = requested_email
        msg_html = render_to_string('api/v1/otp.html', {'name': name,'otp':otp})
        send_mail(subject, msg_plain, from_email,[email_to],html_message=msg_html)
        print('success')
        return super().run()


class SendenduserCreateThread(threading.Thread):
    def __init__(self, record_data):
        self.record_data = record_data
        threading.Thread.__init__(self)

    def run(self) -> None:
        email = self.record_data['email']
        name = self.record_data['full_name']
        # password = self.record_data['password']
        msg_plain = 'Grassroot Marketplace'
        subject = 'Welcome To Grassroot Marketplace'
        from_email = settings.EMAIL_HOST_USER
        email_to = email
        msg_html = render_to_string('api/v1/user_create.html', {'name': name,'email':email})
        # email=[email_to]
        send_mail(subject, msg_plain, from_email,[email_to],html_message=msg_html)
        # send_mail(subject, msg_plain, from_email,[email_to], html_message=msg_html)
        return True