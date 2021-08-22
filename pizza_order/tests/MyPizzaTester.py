import json
from datetime import datetime

from httmock import urlmatch

from core.MyTestCase import MyTestCase


class MyPizzaTester(MyTestCase):

    # Mocks a successfull login to the pizzeria
    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/auth')
    def login_mock(self, caught_url, request):
        tempDict = {'access_token': 'access_token'}
        return {
            'status_code': 200,
            'content': tempDict
        }

    # Mocks a successfull order sent to the pizzeria
    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/orders')
    def pizza_order_mock(self, caught_url, request):
        caughtDict = json.loads(request.body)
        caughtDict['Order_ID'] = int(caughtDict['Table_No']) - 30000
        now = datetime.now()
        caughtDict['Timestamp'] = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
        return {
            'status_code': 201,
            'content': caughtDict
        }

    # Mocks a successfull deletion of an order to the pizzeria
    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/orders')
    def pizza_delete_mock(self, caught_url, request):
        return {
            'status_code': 200
        }

    # Mocks a failed login with the pizzeria
    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/auth')
    def fail_login_mock(self, caught_url, request):
        return {'status_code': 400}

    # Mocks a bad pizza order to the pizzeria because of the table number
    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/orders')
    def pizza_order_mock_bad_table_number(self, caught_url, request):
        return {'status_code': 409}

    # Mocks a bad pizzeria order because of the table number, but when called
    # the second time it returns successfully since the new table number will be
    # at least 1000 higher than 30000
    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/orders')
    def pizza_order_mock_bad_table_number_once(self, caught_url, request):
        caughtDict = json.loads(request.body)
        if caughtDict['Table_No'] < 31000:
            return {'status_code': 409}
        else:
            return self.pizza_order_mock(caught_url, request)

    # Mocks a bad deletion of an order with the pizzeria
    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/orders')
    def pizza_delete_mock_fail(self, caught_url, request):
        return {
            'status_code': 400
        }

    # Mocks a successfull login to the pizzeria, but with a token named differently
    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/auth')
    def login_mock_bad_token_return(self, caught_url, request):
        tempDict = {'token': 'badly named token'}
        return {
            'status_code': 200,
            'content': tempDict
        }

    # Mocks a successfull login to the pizzeria, but with a badly formed json response
    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/auth')
    def login_mock_bad_json_return(self, caught_url, request):
        tempDict = "poor json"
        return {
            'status_code': 200,
            'content': tempDict
        }