import threading

from django.conf import settings
from django.core.mail import send_mail


def _send_admin_notification(contact):
    try:
        send_mail(
            subject=f'پیام جدید از {contact.name}',
            message=(
                f'یک پیام جدید از فرم تماس دریافت شد:\n\n'
                f'نام: {contact.name}\n'
                f'ایمیل: {contact.email}\n'
                f'تلفن: {contact.phone}\n\n'
                f'پیام:\n{contact.message}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_NOTIFICATION_EMAIL],
            fail_silently=True,
        )
    except Exception as exc:
        print(f'Admin notification email failed: {exc}')


def _send_user_confirmation(contact):
    try:
        send_mail(
            subject='پیام شما دریافت شد — Ali Mashaghi',
            message=(
                f'سلام {contact.name} عزیز،\n\n'
                f'از اینکه با من تماس گرفتید بسیار سپاسگزارم.\n'
                f'پیام شما با موفقیت دریافت شد و در اسرع وقت پاسخ خواهم داد.\n\n'
                f'خلاصه پیام شما:\n'
                f'"{contact.message[:200]}{"..." if len(contact.message) > 200 else ""}"\n\n'
                f'با احترام،\n'
                f'Ali Mashaghi\n'
                f'aliu.mashaghi@gmail.com'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact.email],
            fail_silently=True,
        )
    except Exception as exc:
        print(f'User confirmation email failed: {exc}')


def send_contact_emails_parallel(contact):
    """Send admin notification and user confirmation emails in parallel."""
    threading.Thread(target=_send_admin_notification, args=(contact,), daemon=True).start()
    threading.Thread(target=_send_user_confirmation, args=(contact,), daemon=True).start()
