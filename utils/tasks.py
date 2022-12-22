from django.core.mail.message import EmailMultiAlternatives

from utils.celery_app import celery_app

__all__ = [
    "send_email_task",
]


@celery_app.task(name="utils.tasks.send_email_task")
def send_email_task(subject: str, from_email: str, to_emails: list, html_content: str) -> None:
    """
    Celery tasks must receive all args JSON serializables.
    Send email asynchronously.
    """
    email = EmailMultiAlternatives(
        subject=subject,
        body="",
        from_email=from_email,
        to=to_emails,
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
