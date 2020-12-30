import requests
import json
import numpy as np

from base.constants import UNINORTE_SCHEDULE_SIZE, BIT_MATRIX_DATA_TYPE

class UserError(Exception):
    """ An error caused by user actions """
    pass

class ServerError(Exception):
    """ An error caused by the server """
    pass

class StringSheduleTemplate:

    """

    Defines the algorithm template to retrieve the string schedule from the
    uninorte user

    bit_matrix is a matrix where 1 represent "class time" and 0 "free time"
    string schedule is the representation of this matrix in a string format
    in order to save it in a database 
    
    """

    def __init__(self) -> None:
        self.uninorte_schedule = {}
        self.class_hours = None
        self.bit_matrix = np.zeros(
            shape = UNINORTE_SCHEDULE_SIZE, 
            dtype = BIT_MATRIX_DATA_TYPE
        )
        self.string_schedule = ""

    def get_user_string_schedule(self, username, password):

        response = {
            "status_code": 200,
            "user_string_shedule": "",
            "error_meesage": ""
        }

        try:
            self.find_full_uninorte_schedule(username, password)
            self.class_hours = self.find_class_hours()
            self.build_bit_matrix()
            self.from_bit_matrix_to_string_schedule()
            response["user_string_shedule"] = self.string_schedule
        except UserError as user_error:
            response["status_code"] = 400
            response["error_meesage"] = str(user_error)
        except ServerError as server_error:
            response["status_code"] = 500
            response["error_meesage"] = str(server_error)

        return response


    # The following two methods are implemented by subclasses
    def find_full_uninorte_schedule(self, username, password):
        pass
        
    def find_class_hours(self):
        pass

    def build_bit_matrix(self):

        for index_pair in self.class_hours:
            i = index_pair[0]
            j = index_pair[1]
            self.bit_matrix[i][j] = 1

    def from_bit_matrix_to_string_schedule(self):

        for row in self.bit_matrix:
            for element in row:
                self.string_schedule += str(element)



class APIUserRegister(StringSheduleTemplate):

    UNINORTE_SCHEDULE_API = "https://mihorario.herokuapp.com/api/v1/authentications"

    def __init__(self):

        # I don't know what is the letter for sunday.
        self.day_index = {
            'L': 0,
            'M': 1,
            'I': 2,
            'J': 3,
            'V': 4,
            'S': 5,
        }

        self.start_hour_index = {
            '6:30 AM': 0,
            '7:30 AM': 1,
            '8:30 AM': 2,
            '9:30 AM': 3,
            '10:30 AM': 4,
            '11:30 AM': 5,
            '12:30 PM': 6,
            '1:30 PM': 7,
            '2:30 PM': 8,
            '3:30 PM': 9,
            '4:30 PM': 10,
            '5:30 PM': 11,
            '6:30 PM': 12,
            '7:30 PM': 13,
        }
        
        super().__init__()
    
    def find_full_uninorte_schedule(self, username, password):

        response = requests.post(
            self.UNINORTE_SCHEDULE_API, 
            data={
                "username": username, 
                "password": password
            }
        )

        # Unauthorized
        if response.status_code == 401:
            raise UserError("Usuario o contraseña incorrecta")

        if response.status_code != 200:
            raise ServerError("Lo sentimos un error inesperado ocurrió")

        self.uninorte_schedule = json.loads(response.text)

    def find_class_hours(self):
        for subject in self.uninorte_schedule["data"]:
            for session in subject["sessions"]:
                start_time_string = session["start_time"]
                end_time_string = session["end_time"]

                start_time_index = self.start_hour_index.get(
                    start_time_string, 13
                )
                day_index = self.day_index.get(session["day"], 6)

                yield (start_time_index, day_index)

                if self.is_two_hours_block(start_time_string, end_time_string):
                    yield(start_time_index + 1, day_index)

    def is_two_hours_block(self, start_time_string, end_time_string):

        start_hour = int(start_time_string[:start_time_string.find(":")])
        end_hour = int(end_time_string[:end_time_string.find(":")])

        return end_hour - start_hour == 2


class TestUserRegister(APIUserRegister):

    def __init__(self):
        super().__init__()

    def find_full_uninorte_schedule(self, username, password):
        with open("base/test_schedule.json", 'r', encoding='utf8') as read_file:
            self.uninorte_schedule = json.load(read_file)



register_user_class_type = 'PRODUCTION'

def get_user_register_class():

    """Return a user register class given a register_user_class_type"""

    if register_user_class_type == 'PRODUCTION':
        return APIUserRegister
    else:
        return TestUserRegister

