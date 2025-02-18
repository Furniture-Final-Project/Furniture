import unittest
from source.services.payment_gateway import MockPaymentGateway

class TestMockPaymentGateway(unittest.TestCase):

    def setUp(self):
        """Runs before every test case - Sets up the MockPaymentGateway"""
        self.payment_gateway = MockPaymentGateway()

    def test_charge_success(self):
        """Test that charge() can return True for a successful payment"""
        success_count = 0
        total_runs = 1000  # Run multiple times to verify 80% success rate
        
        for _ in range(total_runs):
            if self.payment_gateway.charge(user_id=1, amount=100.0, payment_method="credit_card"):
                success_count += 1
        
        success_rate = (success_count / total_runs) * 100
        self.assertGreater(success_rate, 75)  # Should be close to 80%

    def test_charge_failure(self):
        """Test that charge() can return False for a failed payment"""
        failure_count = 0
        total_runs = 1000  # Run multiple times to verify 20% failure rate
        
        for _ in range(total_runs):
            if not self.payment_gateway.charge(user_id=1, amount=100.0, payment_method="credit_card"):
                failure_count += 1
        
        failure_rate = (failure_count / total_runs) * 100
        self.assertGreater(failure_rate, 15)  # Should be close to 20%

    def test_charge_negative_amount(self):
        """Test that charge() fails with a negative amount"""
        result = self.payment_gateway.charge(user_id=1, amount=-50.0, payment_method="credit_card")
        self.assertFalse(result)  # Expecting False since negative amounts should not be processed

    def test_charge_zero_amount(self):
        """Test that charge() fails with a zero amount"""
        result = self.payment_gateway.charge(user_id=1, amount=0.0, payment_method="credit_card")
        self.assertFalse(result)  # Expecting False since zero transactions should not be processed

    def test_charge_invalid_payment_method(self):
        """Test that charge() fails with an invalid payment method"""
        result = self.payment_gateway.charge(user_id=1, amount=100.0, payment_method="invalid_method")
        self.assertFalse(result)  # Expecting False since payment method is invalid

    def test_charge_missing_user_id(self):
        """Test that charge() fails when user_id is missing (None)"""
        result = self.payment_gateway.charge(user_id=None, amount=100.0, payment_method="credit_card")
        self.assertFalse(result)  # Expecting False since user_id is missing

if __name__ == '__main__':
    unittest.main()
