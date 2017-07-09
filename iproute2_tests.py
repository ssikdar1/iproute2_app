import os
from app import app
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True 

    def tearDown(self):
        pass

    def test_hello_world(self):
        result = self.app.get('/') 
        self.assertEqual(result.status_code, 200) 

    def test_neighbor(self):
        result = self.app.get('/api/v0/iproute2/neighbor')
        #print result.get_data()
        self.assertEqual(result.status_code, 200) 
    
    def test_route(self):
        result = self.app.get('/api/v0/iproute2/route')
        #print result.get_data()
        self.assertEqual(result.status_code, 200) 

    def test_link(self):
        result = self.app.get('/api/v0/iproute2/link')
        #print result.get_data()
        self.assertEqual(result.status_code, 200) 

    def test_maddr(self):
        result = self.app.get('/api/v0/iproute2/maddr')
        #print result.get_data()
        self.assertEqual(result.status_code, 200) 
    
if __name__ == '__main__':
    unittest.main()
