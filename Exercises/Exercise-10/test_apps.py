import unittest
import product_catalog
import shopping_cart

class TestApps(unittest.TestCase):
    def setUp(self):
        shopping_cart.cart.clear()
        self.catalog = product_catalog.app.test_client()
        self.cart = shopping_cart.app.test_client()

    def test_catalog(self):
        response = self.catalog.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), product_catalog.products)

    def test_empty_cart(self):
        response = self.cart.get('/cart')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_add_cart(self):
        item = {'id': 1, 'name': 'Laptop', 'quantity': 1}
        response = self.cart.post('/cart', json=item)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), [item])
        self.assertEqual(self.cart.get('/cart').get_json(), [item])

    def test_unknown_route(self):
        self.assertEqual(self.catalog.get('/missing').status_code, 404)
        self.assertEqual(self.cart.get('/missing').status_code, 404)

    def test_catalog_rejects_post(self):
        self.assertEqual(self.catalog.post('/products', json={}).status_code, 405)

if __name__ == '__main__':
    unittest.main()
