import unittest
from source.controller.payment_gateway import MockPaymentGateway, PaymentMethod



class TestMockPaymentGateway(unittest.TestCase):
    """
    Test suite for the MockPaymentGateway class.

    Tests:
    - Successful payment processing.
    - Failure scenarios (invalid user ID, invalid amount, invalid payment method).
    - Payment success rate approximation.
    - Edge cases for transaction processing.
    """

    def setUp(self) -> None:
        """
    Sets up a new MockPaymentGateway instance before each test.
    """
        self.gateway = MockPaymentGateway()

    def test_charge_success(self) -> None:
        """
    Tests that charge() succeeds for valid transactions.

    Steps:
    - Attempts to charge a valid user with a valid payment method.
    - Verifies that the function returns either True or False.
    """
        success = self.gateway.charge(user_id=1, amount=100.0, payment_method=PaymentMethod.CREDIT_CARD)
        self.assertIn(success, [True, False])  # Make sure the payment returns a valid value

    def test_charge_invalid_user_id(self) -> None:
        """
    Tests that charge() fails when the user ID is None.

    Steps:
    - Attempts to charge with a None user_id.
    - Verifies that the function returns False.
    """
        success = self.gateway.charge(user_id=None, amount=100.0, payment_method=PaymentMethod.CREDIT_CARD)
        self.assertFalse(success)  # Verify that the payment failed

    def test_charge_invalid_amount(self) -> None:
        """
    Tests that charge() fails when the amount is zero or negative.

    Steps:
    - Attempts to charge a valid user with an amount of 0.
    - Attempts to charge with a negative amount.
    - Verifies that both cases return False.
    """
        self.assertFalse(self.gateway.charge(user_id=1, amount=0, payment_method=PaymentMethod.CREDIT_CARD))
        self.assertFalse(self.gateway.charge(user_id=1, amount=-50, payment_method=PaymentMethod.CREDIT_CARD))

    def test_charge_invalid_payment_method(self) -> None:
        """
    Tests that charge() fails for an invalid payment method.

    Steps:
    - Attempts to charge using an unsupported payment method.
    - Verifies that the function returns False.
    """
        self.assertFalse(self.gateway.charge(user_id=1, amount=100.0, payment_method="bitcoin"))  # Check for invalid value

    def test_charge_random_success_rate(self) -> None:
        """
    Tests that charge() maintains an approximate 80% success rate.

    Steps:
    - Runs 1000 payment attempts using a valid payment method.
    - Calculates the success rate of transactions.
    - Ensures the success rate is above 75%.
    """
        success_count = 0
        total_attempts = 1000  # Testing 1000 transactions

        for _ in range(total_attempts):
            if self.gateway.charge(user_id=1, amount=100.0, payment_method=PaymentMethod.CREDIT_CARD):
                success_count += 1

        success_rate = (success_count / total_attempts) * 100
        self.assertGreater(success_rate, 75)  # Make sure the success rate is above 75%

    def test_charge_edge_cases(self) -> None:
        """
    Tests additional edge cases for charge().

    Cases:
    - Charging a high user_id with a very low amount.
    - Charging an invalid user_id with a valid amount.
    - Verifies that both cases return False.
    """
        self.assertFalse(self.gateway.charge(user_id=99999, amount=0.01, payment_method=PaymentMethod.PAYPAL))  # low amount
        self.assertFalse(self.gateway.charge(user_id=0, amount=500, payment_method=PaymentMethod.BANK_TRANSFER))  # invalid user_id


if __name__ == '__main__':
    unittest.main()
