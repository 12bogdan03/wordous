from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import Group

from .tokens import account_activation_token


def send_activation_email(request, user):
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    subject = 'Wordous. Активація акаунта'
    message = render_to_string('accounts/account_activation_email.html', {
        'user': user,
        'protocol': protocol,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
        'token': account_activation_token.make_token(user)
    })
    user.email_user(subject, message)


def check_groups_exist():
    """
    Checks if Groups 'Client' and 'Worker' exist.
    If no, creates them.
    """
    try:
        Group.objects.get(name='Client')
    except Group.DoesNotExist:
        client_group = Group(name='Client')
        client_group.save()

    try:
        Group.objects.get(name='Worker')
    except Group.DoesNotExist:
        worker_group = Group(name='Worker')
        worker_group.save()
