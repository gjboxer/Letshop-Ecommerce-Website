from ecomm import settings
from django.core.mail import send_mail



def send_account_activation_email(email, email_token):
    subject = 'Your account needs to be verified'
    email_from = settings.EMAIL_HOST
    message = f'Hi, click on the link to activate your account https://http://localhost:8000/accounts/activate/{email_token}'
    print(email_token)
    send_mail(subject, message, email_from, [email])