import json
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.test import APIClient


def create_inmemory_file(file_name="tmp.txt", content=b"", content_type=None):
    stream = BytesIO()
    stream.write(content)
    file = InMemoryUploadedFile(
        stream, None, file_name, content_type, stream.tell(), None
    )
    file.seek(0)
    return file


def get_schedule_data_1(username, password):
    route = "base/tests/test_data/test_schedule_1.json"
    with open(route, "r", encoding="utf8") as read_file:
        return 200, json.load(read_file)


def get_schedule_data_2(username, password):
    return 401, {"testing": "is just for testing"}


def get_schedule_data_3(username, password):
    return 500, {"testing": "is just for testing"}


def get_schedule_data_4(username, password):
    route = "base/tests/test_data/test_schedule_2.json"
    with open(route, "r", encoding="utf8") as read_file:
        return 200, json.load(read_file)


DATA_FUNC_TEMPLATE = "base.tests.test_utils.get_schedule_data_{0}"


class TestsMixin:
    def init(self):

        self.client = APIClient()
        self.json_response = {}
        self.print_output = True

    def send_request(self, request_method, *args, **kwargs):
        request_func = getattr(self.client, request_method)
        status_code = None

        if "multipart" not in kwargs:
            if "content_type" not in kwargs and request_method != "get":
                kwargs["content_type"] = "application/json"
                if "data" in kwargs:
                    data = kwargs.get("data", "")
                    kwargs["data"] = json.dumps(data)
        else:
            kwargs.pop("multipart")

        if "status_code" in kwargs:
            status_code = kwargs.pop("status_code")

        if "token" in kwargs:
            kwargs["HTTP_AUTHORIZATION"] = "Bearer %s" % kwargs.pop("token")

        self.response = request_func(*args, **kwargs)

        is_json = False
        if "content-type" in self.response._headers:
            content_types = self.response._headers["content-type"]
            is_json = "application/json" in content_types

        if is_json and self.response.content:
            self.json_response = self.response.json()
            if self.print_output:
                print(json.dumps(self.json_response, indent=4, ensure_ascii=False))

        if status_code:
            assert self.response.status_code == status_code

        return self.response

    def post(self, *args, **kwargs):
        return self.send_request("post", *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.send_request("get", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.send_request("put", *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.send_request("patch", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.send_request("delete", *args, **kwargs)

    def compare_json_response_given_data(self, data: dict, oppositive=False):
        for data_key in data.keys():
            if oppositive:
                assert self.json_response[data_key] != data[data_key]
            else:
                assert self.json_response[data_key] == data[data_key]


class InstanceAssertionsMixin:
    """
    ORM-related assertions for testing instance creation and deletion.
    Copy from https://github.com/sunscrapers/djet/blob/master/djet/assertions.py
    """

    def assert_instance_exists(self, model_class, **kwargs):
        try:
            obj = model_class._default_manager.get(**kwargs)
            self.assertIsNotNone(obj)
        except model_class.DoesNotExist:
            raise AssertionError(
                "No {0} found matching the criteria.".format(
                    model_class.__name__,
                )
            )

    def assert_instance_does_not_exist(self, model_class, **kwargs):
        try:
            instance = model_class._default_manager.get(**kwargs)
            raise AssertionError(
                "A {0} was found matching the criteria. ({1})".format(
                    model_class.__name__,
                    instance,
                )
            )
        except model_class.DoesNotExist:
            pass
