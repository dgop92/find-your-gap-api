from django.db import models


class UninorteUser(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    schedule = models.CharField(max_length=98)  # 14x7 = 98
    created_at = models.DateField(auto_now_add=True)

    # register by password means that you're verified
    # manual or temporal registration means that you're unverified
    # and your record will be deleted on a week
    verified = models.BooleanField(default=False)

    objects = models.Manager()
