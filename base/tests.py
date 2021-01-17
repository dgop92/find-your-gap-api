import json

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from base.models import UninorteUser
from base.urls import results_view_name, register_view_name
from django.urls import reverse

import base.register_user

class TestsMixin:
    
    def init(self):

        self.client = APIClient()
        self.json_response = {}
        self.print_output = True

    def send_request(self, request_method, *args, **kwargs):
        request_func = getattr(self.client, request_method)
        status_code = None

        if 'content_type' not in kwargs and request_method != 'get':
            kwargs['content_type'] = 'application/json'

        if 'data' in kwargs and request_method != 'get' and \
            kwargs['content_type'] == 'application/json':
            
            data = kwargs.get('data', '')
            kwargs['data'] = json.dumps(data)

        if 'status_code' in kwargs:
            status_code = kwargs.pop('status_code')

        self.response = request_func(*args, **kwargs)

        is_json = bool(
            'content-type' in self.response._headers and
            [x for x in self.response._headers['content-type'] if 'json' in x]
        )

        if is_json and self.response.content:
            self.json_response = self.response.json()
            if self.print_output:
                print(json.dumps(
                    self.json_response, indent=4, ensure_ascii=False
                ))

        if status_code:
            assert self.response.status_code == status_code

        return self.response

    def post(self, *args, **kwargs):
        return self.send_request('post', *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.send_request('get', *args, **kwargs)
    
    def compare_json_response_given_data(self, data, 
        oppositive = False):

        for data_key in data.keys():
            if oppositive:
                assert self.json_response[data_key] != data[data_key]
            else:
                assert self.json_response[data_key] == data[data_key]


class TestRegister(TestsMixin, TestCase):

    def setUp(self):
        self.init()

        self.register_url = reverse(register_view_name)


    def test_positive_register(self):

        data = {
            "username": "some_username",
            "password": "password",
            "password_confirmation": "password"
        }

        base.register_user.register_user_class_type = "TEST"

        self.post(
            self.register_url,
            data = data,
            status_code = status.HTTP_201_CREATED
        )

    def test_mismatch_password(self):

        data = {
            "username": "some_username",
            "password": "password",
            "password_confirmation": "no_same_password"
        }

        self.post(
            self.register_url,
            data = data,
            status_code = status.HTTP_400_BAD_REQUEST
        )

    
class TestResults(TestsMixin, TestCase):

    def setUp(self):

        self.init()

        self.results_url = reverse(results_view_name)

        UninorteUser.objects.create(
            username = "my_user_1",
            schedule = "00100001110000110100001010001100000101000000000000000000011100001110000000000000000000000000000000"
        )

        UninorteUser.objects.create(
            username = "my_user_2",
            schedule = "00100001110000110100001010001100000111000000010001000000011100001110000000000000000000000000000000"
        )

    def test_postive_results(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"]
        }

        self.post(
            self.results_url, 
            data = data, 
            status_code = status.HTTP_200_OK
        )

    def test_results_without_sd(self):
        
        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "compute_sd": False
        }

        self.post(
            self.results_url, 
            data = data, 
            status_code = status.HTTP_200_OK
        )

    def test_results_with_limit(self):

        data = {
            "usernames": ["my_user_1", "my_user_2"],
            "limit": 5
        }

        self.post(
            self.results_url, 
            data = data, 
            status_code = status.HTTP_200_OK
        )

        assert self.json_response["count"] == 5

    def common_negative_test_generator(self, data):

        self.post(
            self.results_url, 
            data = data, 
            status_code = status.HTTP_400_BAD_REQUEST
        )

    def test_invalid_user(self):

        data = {
            "usernames": ["my_user_1", "my_user_2", "im bob", "willyrex"]
        }

        self.common_negative_test_generator(data = data)

    def test_not_enought_users(self):

        data = {
            "usernames": ["my_user_1", ]
        }

        self.common_negative_test_generator(data = data)

    def test_empty_list(self):

        data = {
            "usernames": []
        }

        self.common_negative_test_generator(data = data)

    def test_empty_body(self):

        self.common_negative_test_generator(data = {})