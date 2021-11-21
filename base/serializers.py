from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from base.core.finder import GapFinder
from base.core.register_user import APIUserRegister, StringScheduleProcessor
from base.models import UninorteUser


class RegisterSerializer(serializers.Serializer):

    username = serializers.CharField(
        min_length=1,
        max_length=30,
        validators=[
            UniqueValidator(
                queryset=UninorteUser.objects.all(),
                message=_("El usuario ingresado ya fue registrado"),
            )
        ],
    )

    password = serializers.CharField(max_length=80)
    password_confirmation = serializers.CharField(max_length=80)

    string_schedule = serializers.CharField(
        min_length=98, max_length=98, required=False
    )

    def validate(self, data):
        passwd = data["password"]
        passwd_conf = data["password_confirmation"]
        if passwd != passwd_conf:
            raise serializers.ValidationError(_("Las contraseñas no coinciden"))

        data.pop("password_confirmation")

        if "string_schedule" not in data:

            user_register = APIUserRegister(data)
            string_schedule_processor = StringScheduleProcessor(user_register)
            string_schedule_processor.find_user_string_schedule()

            if not string_schedule_processor.is_string_schedule_retrieved():
                raise serializers.ValidationError(
                    _(string_schedule_processor.error_message)
                )

            data["string_schedule"] = string_schedule_processor.string_schedule

        return data

    def create(self, validate_data):

        UninorteUser.objects.create(
            username=validate_data["username"],
            schedule=validate_data["string_schedule"],
        )

        data = {
            "username": validate_data["username"],
            "schedule": validate_data["string_schedule"],
        }

        return data


class UsersSerializer(serializers.Serializer):

    usernames = serializers.ListField(
        child=serializers.CharField(min_length=1, max_length=30),
        allow_empty=False,
        min_length=2,
        max_length=30,
        error_messages={
            "not_a_list": _(
                'Se esperaba una lista de items pero se obtuvo el tipo "{input_type}".'
            ),
            "empty": _("Debes ingresar por lo menos dos usuarios para ver resultados"),
            "min_length": _("Asegúrate de que ingreses mas de {min_length} usuarios."),
            "max_length": _("No soportamos más de {max_length} usuarios."),
        },
    )

    compute_sd = serializers.BooleanField(default=True)

    limit = serializers.IntegerField(min_value=2, required=False)

    def validate_usernames(self, usernames):
        users_not_found = []
        for username in usernames:
            try:
                UninorteUser.objects.get(username=username)
            except UninorteUser.DoesNotExist:
                users_not_found.append(username)

        if users_not_found:
            raise serializers.ValidationError(
                _(
                    "Los siguientes usuarios no se encontraron {users}".format(
                        users=", ".join(users_not_found)
                    )
                )
            )

        return usernames

    def create(self, validate_data):
        strings_shedules = []
        for username in validate_data["usernames"]:
            user = UninorteUser.objects.get(username=username)
            strings_shedules.append(user.schedule)

        gap_finder = GapFinder(strings_shedules, compute_sd=validate_data["compute_sd"])
        gap_finder.find_gaps()
        limit = validate_data["limit"] if "limit" in validate_data else None
        gap_finder.apply_filters(limit=limit)

        gaps = gap_finder.get_results()

        results = {"count": len(gaps), "gaps": gap_finder.get_results()}

        return results


class UninorteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UninorteUser
        fields = ("username", "schedule")
