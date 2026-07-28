import logging
import time

from django.conf import settings
from django.core.mail import EmailMessage, get_connection


logger = logging.getLogger(__name__)


def send_contact_emails(contact, max_attempts=3):
    """Send both contact emails through one SMTP connection, with retries."""
    emails = [
        EmailMessage(
            subject=f'پیام جدید فرم تماس از {contact.name}',
            body=(
                f'یک پیام جدید از طریق فرم تماس وب‌سایت دریافت شده است:\n\n'
                f'نام: {contact.name}\n'
                f'ایمیل: {contact.email}\n'
                f'تلفن: {contact.phone}\n\n'
                f'متن پیام:\n{contact.message}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_NOTIFICATION_EMAIL],
            reply_to=[contact.email],
        ),
        EmailMessage(
            subject='پیام شما دریافت شد — علی مشاغی',
            body=(
                f'سلام {contact.name} عزیز،\n\n'
                f'از اینکه با من تماس گرفتید، بسیار سپاسگزارم.\n'
                f'پیام شما با موفقیت دریافت شد و در اسرع وقت پاسخ خواهم داد.\n\n'
                f'خلاصه پیام شما:\n'
                f'"{contact.message[:200]}{"..." if len(contact.message) > 200 else ""}"\n\n'
                f'با احترام،\n'
                f'علی مشاغی\n'
                f'{settings.DEFAULT_FROM_EMAIL}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[contact.email],
        ),
    ]

    for attempt in range(1, max_attempts + 1):
        try:
            with get_connection(fail_silently=False) as connection:
                sent_count = connection.send_messages(emails)
            if sent_count != len(emails):
                raise RuntimeError(
                    f'Expected to send {len(emails)} emails, but sent {sent_count}.'
                )
            return sent_count
        except Exception:
            logger.exception(
                'Contact email attempt %s of %s failed.',
                attempt,
                max_attempts,
            )
            if attempt == max_attempts:
                raise
            time.sleep(attempt)
