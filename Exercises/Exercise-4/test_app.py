import unittest
from app import app


class AboutAPITest(unittest.TestCase):
    def test_about(self):
        with app.test_client() as client:
            response = client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertEqual(response.json, {
            'name': 'Simple REST API', 'version': '1.0',
            'description': 'This is a simple REST API built with Flask.'})

    def test_unknown_route(self):
        with app.test_client() as client:
            self.assertEqual(client.get('/missing-route').status_code, 404)

    def test_post_not_allowed(self):
        with app.test_client() as client:
            self.assertEqual(client.post('/about').status_code, 405)


if __name__ == '__main__':
    unittest.main(verbosity=2)
