import random

from base.models import UninorteUser

random.seed(10)


def get_random_schedule():
    options = ["0", "0", "0", "1"]
    return "".join([random.choice(options) for _ in range(98)])


def get_random_user(user_id):
    return UninorteUser.objects.create(
        username=f"my_user_{user_id}",
        schedule=get_random_schedule(),
    )
