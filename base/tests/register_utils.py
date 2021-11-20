import json


def get_api_register_data(username, password):
    with open("base/tests/test_schedule.json", "r", encoding="utf8") as read_file:
        return 200, json.load(read_file)
