from django.db import models


class UninorteUser(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    schedule = models.CharField(max_length=98)  # 14x7 = 98

    objects = models.Manager()
