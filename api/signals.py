from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.conf import settings

from .models import Lessons


@receiver(post_save, sender=Lessons)
def send_mail(sender, instance, created, **kwargs):
    '''
    send_mail - Lessons modeliga yangi ma'lumot qo'shilganida foydalanuvchilarni email manziliga xabar yuboriladi.
    '''

    if created:
        subject = "You have been assigned a house."
        from_email = settings.DEFAULT_FROM_EMAIL

        recipient_list = list(User.objects.filter(email__isnull=False).values_list('email', flat=True))

        if recipient_list:
            html_content = render_to_string('emails/index.html', {
                'title': instance.title,
                'description': instance.description or "Ma'lumot qo'shilmadi.",
                'is_active': instance.is_active,
            })

            email = EmailMultiAlternatives(
                subject=subject,
                from_email=from_email,
                to=recipient_list
            )

            email.attach_alternative(html_content, 'text/html')
            email.send(fail_silently=True)


