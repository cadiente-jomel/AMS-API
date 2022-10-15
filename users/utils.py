import os
from typing import Any
from threading import Thread
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse


def profile_directory_path(instance: "User", filename: str) -> str:
    """Create a directory path to upload the User's Image
    :param object instance:
        The instance where the current file is being attached.
    :param str filename:
        The filename that was originally given to the file.
        This may not be taken into account when determining
        the final destination path
    :result str: Directory path.file_extension.
    """

    image_name, extension = os.path.splitteext(filename)
    name = instance.get_full_name.lower().replace(" ", "_")
    return f"profiles/{name}/{image_name}{extension}"


class EmailThread(Thread):
    def __init__(self, email):
        self.email = email
        Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    def get_absolute_url(self, access_token: str, request: Any) -> str:
        current_domain_name = get_current_site(request).domain
        relative_path = reverse("users:verify-email")
        absolute_url = f"{request.scheme}:/{current_domain_name}/{relative_path}?token={access_token}"

        return absolute_url

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["email_subject"], body=data["email_body"], to=[data["send_to"]]
        )
        EmailThread(email).start()
