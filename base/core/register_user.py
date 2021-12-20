import json

import requests
from django.conf import settings
from django.utils.module_loading import import_string

from base.core.constants import DAYS_PER_WEEK


def get_schedule_data_function():
    return import_string(settings.SCHEDULE_DATA_FUNCTION)


class RegisterUserError(Exception):
    """ An error caused while trying to register a user """

    pass


class ClassHoursGetter:
    def __init__(self, request_data=None):
        self.request_data = request_data

    def get_class_hours(self):
        return []


class StringScheduleProcessor:
    def __init__(self, class_hours_getter):
        self.class_hours_getter = class_hours_getter
        self.string_schedule = ""
        self.error_message = ""

    def find_user_string_schedule(self):

        try:
            self.class_hours = self.class_hours_getter.get_class_hours()
            self.find_ss_from_class_hours()
        except RegisterUserError as register_user_error:
            self.error_message = str(register_user_error)
        except Exception:
            self.error_message = "Lo sentimos, ha ocurrido un error inesperado"

    def find_ss_from_class_hours(self):
        ss_list = [0 for _ in range(98)]
        for day_hour in self.class_hours:
            hour_index, day_index = day_hour
            pos = hour_index * DAYS_PER_WEEK + day_index
            ss_list[pos] = 1
        self.string_schedule = "".join(map(str, ss_list))

    def is_string_schedule_retrieved(self):
        return self.string_schedule != ""


def get_schedule_data_from_uni_api(username, password):
    url = settings.UNINORTE_SCHEDULE_API
    response = requests.post(
        url,
        data={"username": username, "password": password},
    )
    return response.status_code, json.loads(response.text)


def get_schedule_data_for_development(username, password):
    route = "base/tests/test_data/test_schedule_1.json"
    with open(route, "r", encoding="utf8") as read_file:
        return 200, json.load(read_file)


class APIUserRegister(ClassHoursGetter):
    def __init__(self, request_data):
        self.username = request_data["username"]
        self.password = request_data["password"]
        self.uninorte_schedule = {}

        # I don't know what is the letter for sunday.
        self.day_index = {
            "L": 0,
            "M": 1,
            "I": 2,
            "J": 3,
            "V": 4,
            "S": 5,
        }

        self.start_hour_index = {
            "6:30 AM": 0,
            "7:30 AM": 1,
            "8:30 AM": 2,
            "9:30 AM": 3,
            "10:30 AM": 4,
            "11:30 AM": 5,
            "12:30 PM": 6,
            "1:30 PM": 7,
            "2:30 PM": 8,
            "3:30 PM": 9,
            "4:30 PM": 10,
            "5:30 PM": 11,
            "6:30 PM": 12,
            "7:30 PM": 13,
        }

        self.unauthorized_message = "Usuario o contraseña incorrecta"
        self.unexpected_message = "Lo sentimos, un error inesperado ocurrió"

        super().__init__(request_data)

    def find_full_uninorte_schedule(self):

        schedule_data_func = get_schedule_data_function()
        status_code, json_data = schedule_data_func(self.username, self.password)

        # Unauthorized
        if status_code == 401:
            raise RegisterUserError(self.unauthorized_message)

        if status_code != 200:
            raise RegisterUserError(self.unexpected_message)

        self.uninorte_schedule = json_data

    def get_class_hours(self):
        self.find_full_uninorte_schedule()

        class_hours = []

        for subject in self.uninorte_schedule["data"]:
            for session in subject["sessions"]:
                start_time_string = session["start_time"]
                end_time_string = session["end_time"]

                start_time_index = self.start_hour_index.get(start_time_string, 13)
                day_index = self.day_index.get(session["day"], 6)

                class_hours.append((start_time_index, day_index))

                if self.is_two_hours_block(start_time_string, end_time_string):
                    class_hours.append((start_time_index + 1, day_index))

        return class_hours

    @staticmethod
    def is_two_hours_block(start_time_string, end_time_string):

        start_hour = int(start_time_string[: start_time_string.find(":")])
        end_hour = int(end_time_string[: end_time_string.find(":")])

        if start_time_string[-2:] == "PM" and start_hour != 12:
            start_hour += 12

        if end_time_string[-2:] == "PM" and end_hour != 12:
            end_hour += 12

        return end_hour - start_hour == 2


class ManualRegisterGetter(ClassHoursGetter):
    def __init__(self, request_data=None):
        self.list_of_indices = request_data["list_of_indices"]
        super().__init__(request_data=request_data)

    def get_class_hours(self):
        return self.list_of_indices
