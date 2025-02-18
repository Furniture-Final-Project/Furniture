import random

class MockPaymentGateway:
    def charge(self, user_id: int, amount: float, payment_method: str) -> bool:
        """
        Simulates a payment transaction.
        
        :param user_id: The ID of the user making the payment.
        :param amount: The total amount to be charged.
        :param payment_method: The selected payment method (e.g., "credit_card").
        :return: True if payment is successful, False otherwise.
        """

        # ✅ Reject invalid input cases
        if user_id is None or amount <= 0 or payment_method not in ["credit_card", "paypal", "bank_transfer"]:
            print("❌ Invalid transaction detected!")
            return False

        print(f"Processing mock payment for User {user_id}: ${amount} via {payment_method}")

        # Simulate payment success or failure (80% success rate)
        payment_success = random.random() < 0.8  # 80% probability of success

        if payment_success:
            print("✅ Payment successful!")
        else:
            print("❌ Payment failed!")

        return payment_success
