import unittest
from app import app


class FlaskRoutesTest(unittest.TestCase):
    def test_home_response(self):
        with app.test_client() as client:
            response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'Hello from Flask on Kubernetes!')

    def test_unknown_route(self):
        with app.test_client() as client:
            self.assertEqual(client.get('/missing-route').status_code, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
