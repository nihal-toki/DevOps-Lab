import unittest
from app import app


class FlashSaleTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Welcome to Big Sale!')
        self.assertTrue(response.json['pod'])
        self.assertIsInstance(response.json['ts'], (int, float))

    def test_purchase_with_user(self):
        response = self.client.get('/buy?user=lab-test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(response.json['user'], 'lab-test')
        self.assertIn(response.json['item'], ['Smartphone', 'Shoes', 'Headphones', 'Laptop'])
        self.assertTrue(response.json['served_by_pod'])

    def test_purchase_default_user(self):
        response = self.client.get('/buy')
        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.json['user'], r'^user\d+$')

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'healthy')
        self.assertTrue(response.json['pod'])

    def test_unknown_route(self):
        self.assertEqual(self.client.get('/missing-route').status_code, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
