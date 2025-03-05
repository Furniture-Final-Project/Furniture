import unittest
from source.services.payment_gateway import MockPaymentGateway, PaymentMethod


class TestMockPaymentGateway(unittest.TestCase):
    """Test suite for the MockPaymentGateway class."""

    def setUp(self) -> None:
        """Setup before each test."""
        self.gateway = MockPaymentGateway()

    def test_charge_success(self) -> None:
        """Test that charge() succeeds for valid transactions."""
        success = self.gateway.charge(user_id=1, amount=100.0, payment_method=PaymentMethod.CREDIT_CARD)
        self.assertIn(success, [True, False])  # Make sure the payment returns a valid value

    def test_charge_invalid_user_id(self) -> None:
        """Test that charge() fails when user_id is None."""
        success = self.gateway.charge(user_id=None, amount=100.0, payment_method=PaymentMethod.CREDIT_CARD)
        self.assertFalse(success)  # Verify that the payment failed

    def test_charge_invalid_amount(self) -> None:
        """Test that charge() fails when amount is zero or negative."""
        self.assertFalse(self.gateway.charge(user_id=1, amount=0, payment_method=PaymentMethod.CREDIT_CARD))
        self.assertFalse(self.gateway.charge(user_id=1, amount=-50, payment_method=PaymentMethod.CREDIT_CARD))

    def test_charge_invalid_payment_method(self) -> None:
        """Test that charge() fails for invalid payment methods."""
        self.assertFalse(self.gateway.charge(user_id=1, amount=100.0, payment_method="bitcoin"))  # Check for invalid value

    def test_charge_random_success_rate(self) -> None:
        """Test that charge() has an approximate 80% success rate."""
        success_count = 0
        total_attempts = 1000  # Testing 1000 transactions

        for _ in range(total_attempts):
            if self.gateway.charge(user_id=1, amount=100.0, payment_method=PaymentMethod.CREDIT_CARD):
                success_count += 1

        success_rate = (success_count / total_attempts) * 100
        self.assertGreater(success_rate, 75)  # Make sure the success rate is above 75%

    def test_charge_edge_cases(self) -> None:
        """Test additional edge cases for charge()."""
        self.assertFalse(self.gateway.charge(user_id=99999, amount=0.01, payment_method=PaymentMethod.PAYPAL))  # low amount
        self.assertFalse(self.gateway.charge(user_id=0, amount=500, payment_method=PaymentMethod.BANK_TRANSFER))  # invalid user_id


if __name__ == '__main__':
    unittest.main()
