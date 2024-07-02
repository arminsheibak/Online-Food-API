from django.db.models.signals import post_save
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(post_save, sender=get_user_model())
def send_welcome_email(sender, instance,**kwargs):
    subject = 'Welcome to Little Lemon'
    message = 'Thank you for signing up to our site!'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [instance.email]
    try:
        send_mail(subject, message, email_from, recipient_list)
    except BadHeaderError:
        pass
