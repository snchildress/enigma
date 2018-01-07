from django.db import models

from datetime import datetime, timedelta
from encrypted_model_fields.fields import EncryptedTextField
from pytz import utc
import uuid


def calculate_expiration_timestamp():
    """Automatically set any new Secret record to expire in 7 days"""
    expiration_timestamp = datetime.now(utc) + timedelta(days=7)
    return expiration_timestamp


class Secret(models.Model):
    message = EncryptedTextField('Encrypted Message')
    uuid = models.UUIDField('UUID', default=uuid.uuid4, editable=False)
    create_timestamp = models.DateTimeField('Creation Date',
                                             auto_now_add=True)
    update_timestamp = models.DateTimeField('Last Updated Date',
                                             auto_now=True)
    expiration_timestamp = models.DateTimeField(
        'Expiration Date',
        default=calculate_expiration_timestamp()
    )

    def __str__(self):
        return str(self.uuid) + ': ' + str(self.create_timestamp)

    class Meta:
        db_table = 'secrets'
        verbose_name_plural = 'Secrets'
