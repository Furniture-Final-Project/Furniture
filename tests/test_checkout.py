import unittest
from source.models.checkout import Checkout

class TestCheckout(unittest.TestCase):

    def setUp(self):
        """Runs before every test case"""
        self.checkout = Checkout(user_id=1, address="123 Main St", payment_method="credit_card")

    def test_checkout_initialization(self):
        """Test if Checkout initializes correctly"""
        self.assertEqual(self.checkout.user_id, 1)
        self.assertEqual(self.checkout.address, "123 Main St")
        self.assertEqual(self.checkout.payment_method, "credit_card")

    def test_checkout_default_order(self):
        """Test if order is None by default when Checkout is created"""
        self.assertIsNone(self.checkout.order)  # ✅ Expecting None at initialization

    def test_set_order(self):
        """Test if set_order correctly assigns an order (mocked)"""
        class MockOrder:
            pass  # A simple mock to replace the real Order class
        
        order = MockOrder()  # Using a fake Order since we don’t have the real one yet
        self.checkout.set_order(order)
        
        self.assertEqual(self.checkout.order, order)

if __name__ == '__main__':
    unittest.main()
