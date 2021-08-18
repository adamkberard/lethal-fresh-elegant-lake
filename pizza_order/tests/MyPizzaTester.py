import json

from httmock import urlmatch

from core.MyTestCase import MyTestCase


class MyPizzaTester(MyTestCase):
    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/auth')
    def login_mock(self, caught_url, request):
        tempDict = {'access_token': 'access_token'}
        return {
            'status_code': 200,
            'content': tempDict
        }

    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/orders')
    def pizza_order_mock(self, caught_url, request):
        caughtDict = json.loads(request.body)
        caughtDict['Order_ID'] = int(caughtDict['Table_No']) - 30000
        caughtDict['Timestamp'] = "2021-08-16T02:37:41.353941"
        return {
            'status_code': 201,
            'content': caughtDict
        }

    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/auth')
    def fail_login_mock(self, caught_url, request):
        return {'status_code': 400}

    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/orders')
    def pizza_order_mock_bad_table_number(self, caught_url, request):
        return {'status_code': 409}

    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/orders')
    def pizza_order_mock_bad_table_number_once(self, caught_url, request):
        caughtDict = json.loads(request.body)
        # Only mock the first bad attempt
        if caughtDict['Table_No'] == 300001:
            return {'status_code': 409}
        else:
            return self.pizza_order_mock(caught_url, request)
