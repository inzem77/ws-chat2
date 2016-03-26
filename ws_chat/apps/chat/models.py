from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Message(models.Model):
    message = models.CharField(max_length=255)
    session_key = models.CharField(max_length=32)
    other_session_key = models.CharField(max_length=32)
    dt = models.DateTimeField(auto_created=True)


