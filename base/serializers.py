from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from base.core.analyze_meetings import get_schedule_meeting_data
from base.core.constants import DAYS
from base.core.distance_algorithms import get_distance_matrix_from_string_schedule
from base.core.finder import (
    DEFAULT_MATRIX_COMPUTER_OPTIONS,
    DistanceMatrixComputer,
    GapFinder,
)
from base.core.gap_filters import filter_by_days, limit_results
from base.core.register_user import (
    APIUserRegister,
    AutomaticRegisterGetter,
    StringScheduleProcessor,
)
from base.custom_validators import FileExtensionValidator
from base.models import UninorteUser


def get_string_schedules_from_username(usernames):
    users_not_found = []
    string_schedules = []
    for username in usernames:
        try:
            user = UninorteUser.objects.get(username=username)
            string_schedules.append(user.schedule)
        except UninorteUser.DoesNotExist:
            users_not_found.append(username)
    return string_schedules, users_not_found


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
        min_length=1,
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

        if "days_to_filter" in validated_data:
            gap_finder.apply_filter(filter_by_days, validated_data["days_to_filter"])
        if "limit" in validated_data:
            gap_finder.apply_filter(limit_results, limit=validated_data["limit"])

        gaps = gap_finder.get_results()

        results = {"count": len(gaps), "gaps": gap_finder.get_results()}

        return results


class MeetingSerializer(serializers.Serializer):

    usernames_file = serializers.FileField(
        required=False, validators=[FileExtensionValidator(allowed_extensions=["txt"])]
    )

    # username length is roughly 20-30, so by list you can only sent 40
    extra_usernames = serializers.ListField(
        required=False,
        child=serializers.CharField(min_length=1, max_length=30),
        allow_empty=True,
        max_length=30,
        error_messages={
            "not_a_list": _(
                'Se esperaba una lista de items pero se obtuvo el tipo "{input_type}".'
            ),
            "max_length": _(
                "No soportamos más de 40 usuarios, Si deseas analizar un gran número de estudiantes es recomendado usar la opción de subir archivo"
            ),
        },
    )

    username_to_filter = serializers.CharField(
        min_length=1, max_length=30, required=False
    )

    def validate_usernames_file(self, file):
        MAX_FILE_SIZE = 10_000
        # file is not required, so it may be empty
        if file and file.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                _(
                    "El tamaño del archivo es demasiado grande, Asegúrate de que pese menos de 10KB"
                )
            )
        return file

    def validate_username_to_filter(self, username):
        try:
            if username:
                UninorteUser.objects.get(username=username)
        except UninorteUser.DoesNotExist:
            raise serializers.ValidationError(
                _("El usuario para filtrar el horario no existe")
            )
        return username

    def validate(self, data):
        if "usernames_file" not in data and "extra_usernames" not in data:
            raise serializers.ValidationError(
                _("Al menos debes proporcionar una forma para obtener los usuarios")
            )

        final_ss = []
        users_not_found = []
        if "usernames_file" in data:
            file = data["usernames_file"]
            try:
                content = file.read().decode("utf-8")
                usernames = content.splitlines()
                # ss = string schedules
                ss, users_not_found1 = get_string_schedules_from_username(usernames)
                final_ss.extend(ss)
                users_not_found.extend(users_not_found1)
            except UnicodeDecodeError:
                raise serializers.ValidationError(
                    _("Parece que el archivo proporcionado no es texto")
                )

        if "extra_usernames" in data:
            extra_users = data["extra_usernames"]
            extra_ss, users_not_found2 = get_string_schedules_from_username(extra_users)
            final_ss.extend(extra_ss)
            users_not_found.extend(users_not_found2)

        if len(final_ss) < 2:
            raise serializers.ValidationError(
                _(
                    "Algunos usuarios no se encontraron, por ende no se puede realizar el análisis"
                )
            )

        data["final_ss"] = final_ss
        data["users_not_found"] = users_not_found

        return data

    def create(self, validated_data):
        final_ss = validated_data["final_ss"]
        if "username_to_filter" in validated_data:
            ss_to_filter = UninorteUser.objects.get(
                username=validated_data["username_to_filter"]
            ).schedule
        else:
            ss_to_filter = None
        return get_schedule_meeting_data(final_ss, ss_to_filter)


class AutomaticRegisterSerializer(serializers.Serializer):

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

    list_of_indices = serializers.ListField(
        child=serializers.ListField(
            child=serializers.IntegerField(max_value=100, min_value=-100),
            max_length=2,
            min_length=2,
        ),
        allow_empty=False,
        max_length=98,
        error_messages={
            "not_a_list": _(
                'Se esperaba una lista de items pero se obtuvo el tipo "{input_type}".'
            ),
            "empty": _("El horario no puede estar vacío"),
            "max_length": _("Es imposible tener más de 98 horas de clases a la semana"),
        },
    )

    def validate_list_of_indices(self, raw_list_of_indices):

        for day_hour in raw_list_of_indices:
            hour_index, day_index = day_hour
            if not (0 <= day_index <= 6):
                raise serializers.ValidationError(
                    _("El índice del día debe estar entre 0 y 6")
                )
            if not (0 <= hour_index <= 12):
                raise serializers.ValidationError(
                    _("El índice de la hora debe estar entre 0 y 12")
                )

        return raw_list_of_indices

    def create(self, validated_data):
        string_schedule_processor = StringScheduleProcessor(
            AutomaticRegisterGetter(validated_data)
        )
        # is not necessary to validate the data because we receive the list immediately
        string_schedule_processor.find_user_string_schedule()
        username = validated_data["username"]
        string_schedule = string_schedule_processor.string_schedule

        UninorteUser.objects.create(
            username=username,
            schedule=string_schedule,
        )

        data = {
            "username": username,
            "schedule": string_schedule,
        }

        return data


class UninorteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UninorteUser
        fields = ("username", "schedule")
