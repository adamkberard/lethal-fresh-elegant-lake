import json

from django.test import TestCase


class MyTestCase(TestCase):

    # Ok
    def assertResponse200(self, response):
        self.assertEqual(response.status_code, 200)

    # Created
    def assertResponse201(self, response):
        self.assertEqual(response.status_code, 201)

    # No Content
    def assertResponse204(self, response):
        self.assertEqual(response.status_code, 204)

    # Created
    def assertResponse400(self, response):
        self.assertEqual(response.status_code, 400)

    # Unauthorized
    def assertResponse401(self, response):
        self.assertEqual(response.status_code, 401)

    # Not found
    def assertResponse404(self, response):
        self.assertEqual(response.status_code, 404)

    def loadJSONSafely(self, response):
        try:
            return json.loads(response.content)
        except ValueError:
            self.fail("Couldn't load the JSON data safely.")

    @classmethod
    def getDictFromBody(self, body):
        dict = {}
        params = body.split("&")
        for param in params:
            paramSplit = param.split("=")
            dict[paramSplit[0]] = paramSplit[1]
        return dict
