from django.template.loader import render_to_string

from utils.tasks import send_email_task

__all__ = [
    "send_email",
]


def send_email(subject: str, from_email: str, to_emails: list, template_path: str, template_context: dict) -> None:
    html_content = render_to_string(template_path, template_context)
    html_content = html_content.replace("\n", "")
    send_email_task.delay(subject, from_email, to_emails, html_content)
