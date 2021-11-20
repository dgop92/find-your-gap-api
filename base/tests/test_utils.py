import json

from rest_framework.test import APIClient


class TestsMixin:
    def init(self):

        self.client = APIClient()
        self.json_response = {}
        self.print_output = True

    def send_request(self, request_method, *args, **kwargs):
        request_func = getattr(self.client, request_method)
        status_code = None

        if "content_type" not in kwargs and request_method != "get":
            kwargs["content_type"] = "application/json"

        if (
            "data" in kwargs
            and request_method != "get"
            and kwargs["content_type"] == "application/json"
        ):

            data = kwargs.get("data", "")
            kwargs["data"] = json.dumps(data)

        if "status_code" in kwargs:
            status_code = kwargs.pop("status_code")

        self.response = request_func(*args, **kwargs)

        is_json = bool(
            "content-type" in self.response._headers
            and [x for x in self.response._headers["content-type"] if "json" in x]
        )

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

    def compare_json_response_given_data(self, data, oppositive=False):

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
