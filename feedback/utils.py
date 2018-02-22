from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_feedback_email(subject, email, message):
    context = {'subject': subject, 'email': email, 'message': message}
    email_subject = render_to_string('feedback/feedback_email_subject.txt',
                                     context)
    email_body = render_to_string('feedback/feedback_email_body.txt', context)

    email = EmailMessage(
        email_subject, email_body, email,
        [settings.DEFAULT_FROM_EMAIL], [],
        headers={'Reply-To': email}
    )
    return email.send(fail_silently=False)
