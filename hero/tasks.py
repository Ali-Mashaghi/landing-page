from celery import shared_task

from hero.models import Contact
from hero.services.email import send_contact_emails


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def send_contact_emails_task(self, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    send_contact_emails(contact)
