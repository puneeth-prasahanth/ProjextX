import unittest
import flask_testing
from flask_testing import TestCase
#from flask.ext.testing import TestCase
from app_flask_session import app

class Testapp(unittest.TestCase):

    #def setup(self):
    #    pass

    def test_root(self):
        tester=app.test_client(self)
        responce=tester.get('/',content_type='html/text')
        self.assertEqual(responce.status_code,200)

    def test_login(self):
        tester=app.test_client(self)
        responce=tester.get('/login',content_type='html/text')
        self.assertEqual(responce.status_code,200)

    def test_correct_login(self):
        tester=app.test_client(self)
        responce=tester.get('/login',
                            data=dict(username="puneeth",password="Passw0rd" )
                            ,follow_redirects=True)
        print(f'Passed')
        self.assertIn(b'Welcome to ProjectX',responce.data)



    def test_logout(self):
        tester=app.test_client(self)
        responce=tester.get('/logout',content_type='html/text')
        self.assertEqual(responce.status_code,200)

    def test_register(self):
        tester=app.test_client(self)
        responce=tester.get('/register',content_type='html/text')
        self.assertEqual(responce.status_code,200)

    def test_location(self):
        tester=app.test_client(self)
        responce=tester.get('/api/v1/location/',content_type='html/text')
        self.assertEqual(responce.status_code,200)

    def test_location_data(self):
        tester=app.test_client(self)
        responce=tester.get('/api/v1/location/?location=Perimeter'
                            ,follow_redirects=True)
        self.assertIn(b'List of Locations',responce.data)

    def test_department(self):
        tester=app.test_client(self)
        responce=tester.get('/api/v1/location/department',content_type='html/text')
        self.assertEqual(responce.status_code,200)

    def test_category(self):
        tester=app.test_client(self)
        responce=tester.get('/api/v1/location/department/category',content_type='html/text')
        self.assertEqual(responce.status_code,200)

    def test_create(self):
        tester=app.test_client(self)
        responce=tester.get('/api/v1/create',content_type='html/text')
        self.assertEqual(responce.status_code,200)

    def test_update(self):
        tester=app.test_client(self)
        responce=tester.get('/api/v1/update',content_type='html/text')
        self.assertEqual(responce.status_code,200)

    def test_compare_meta(self):
        tester=app.test_client(self)
        responce=tester.get('/api/v1/compare_meta',content_type='html/text')
        self.assertEqual(responce.status_code,200)

    def text_exit(self):
        exit(0)




if __name__ == '__main__':
    unittest.main(failfast=True)
