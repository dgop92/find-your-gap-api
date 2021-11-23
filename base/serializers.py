from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from base.core.constants import DAYS
from base.core.distance_algorithms import get_distance_matrix_from_string_schedule
from base.core.finder import (
    DEFAULT_MATRIX_COMPUTER_OPTIONS,
    DistanceMatrixComputer,
    GapFinder,
)
from base.core.gap_filters import filter_by_days, limit_results
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

    # MATRIX_COMPUTER_OPTIONS
    compute_sd = serializers.BooleanField(
        default=DEFAULT_MATRIX_COMPUTER_OPTIONS["compute_sd"]
    )
    no_classes_day = serializers.BooleanField(
        default=DEFAULT_MATRIX_COMPUTER_OPTIONS["no_classes_day"]
    )
    ignore_weekend = serializers.BooleanField(
        default=DEFAULT_MATRIX_COMPUTER_OPTIONS["ignore_weekend"]
    )

    limit = serializers.IntegerField(min_value=2, required=False)
    days_to_filter = serializers.ListField(
        child=serializers.ChoiceField(choices=list(zip([0, 1, 2, 3, 4, 5, 6], DAYS))),
        required=False,
        allow_empty=False,
        min_length=2,
        max_length=7,
    )

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

    def create(self, validated_data):
        string_schedules = []
        for username in validated_data["usernames"]:
            user = UninorteUser.objects.get(username=username)
            string_schedules.append(user.schedule)

        distance_matrices = list(
            map(get_distance_matrix_from_string_schedule, string_schedules)
        )
        distance_matrix_computer = DistanceMatrixComputer(
            distance_matrices,
            options={
                "compute_sd": validated_data["compute_sd"],
                "no_classes_day": validated_data["no_classes_day"],
                "ignore_weekend": validated_data["ignore_weekend"],
            },
        )

        gap_finder = GapFinder(distance_matrix_computer)
        gap_finder.find_gaps()
        if "limit" in validated_data:
            gap_finder.apply_filter(limit_results, limit=validated_data["limit"])
        if "days_to_filter" in validated_data:
            gap_finder.apply_filter(filter_by_days, validated_data["days_to_filter"])

        gaps = gap_finder.get_results()

        results = {"count": len(gaps), "gaps": gap_finder.get_results()}

        return results


class UninorteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UninorteUser
        fields = ("username", "schedule")
