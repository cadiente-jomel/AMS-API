# standard libraries/modules
import os
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from django.db import transaction


# local modules
from users.models import User

load_dotenv()

class Command(BaseCommand):
    help = 'Create super user'

    def handle(self, *args, **kwargs) -> None:
        with transaction.atomic():
            user = User(
                email=str(os.getenv('SU_EMAIL')),
                username=str(os.getenv('SU_USERNAME')),
                first_name=str(os.getenv('SU_FIRSTNAME')), 
                last_name=str(os.getenv('SU_LASTNAME')),
                is_staff=True,
                is_superuser=True,
            ) 
            user.set_password(str(os.getenv('SU_PASSWORD')))
            user.save()
        self.stdout.write('Super user created succesfully.')