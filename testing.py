import unittest
from app import app


class Apptest(unittest.TestCase):
    # testing if endpoint status codes match its method (get/push/...)
    def test_user_register(self):
        test = app.test_client(self)
        response = test.get('/user-registration/')
        status = response.status_code
        self.assertEqual(status, 405)

    def test_email(self):
        test = app.test_client(self)
        response = test.get('/emailsent/testemail@gmail.com')
        status = response.status_code
        self.assertEqual(status, 200)

    def test_viewprofile(self):
        test = app.test_client(self)
        response = test.get('/viewprofile/JesseT/')
        status = response.status_code
        self.assertEqual(status, 200)

    def test_addproduct(self):
        test = app.test_client(self)
        response = test.get('/addtocatalogue/')
        status = response.status_code
        self.assertEqual(status, 405)

    def test_viewproducts(self):
        test = app.test_client(self)
        response = test.get('/viewcatalogue/')
        status = response.status_code
        self.assertEqual(status, 200)

    # checking content type

    def test_type_viewcat(self):
        test = app.test_client(self)
        response = test.get('/viewcatalogue/')
        self.assertEqual(response.content_type, "application/json")