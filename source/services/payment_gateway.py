from enum import Enum
from abc import ABC, abstractmethod
import random


class PaymentMethod(Enum):
    """Enum representing the available payment methods."""

    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class PaymentStrategy(ABC):
    """Abstract base class for payment strategies."""

    @abstractmethod
    def process_payment(self, user_id: int, amount: float) -> bool:
        """
        Processes a payment transaction.

        :param user_id: The ID of the user making the payment.
        :param amount: The total amount to be charged.
        :return: True if payment is successful, False otherwise.
        """
        pass


class CreditCardPayment(PaymentStrategy):
    """Handles credit card transactions."""

    def process_payment(self, user_id: int, amount: float) -> bool:
        return MockPaymentGateway().charge(user_id, amount, PaymentMethod.CREDIT_CARD)


class PayPalPayment(PaymentStrategy):
    """Handles PayPal transactions."""

    def process_payment(self, user_id: int, amount: float) -> bool:
        return MockPaymentGateway().charge(user_id, amount, PaymentMethod.PAYPAL)


class BankTransferPayment(PaymentStrategy):
    """Handles bank transfer transactions."""

    def process_payment(self, user_id: int, amount: float) -> bool:
        return MockPaymentGateway().charge(user_id, amount, PaymentMethod.BANK_TRANSFER)


class MockPaymentGateway:
    """Simulates a payment processing gateway."""

    def charge(self, user_id: int, amount: float, payment_method: PaymentMethod) -> bool:
        """Simulates a payment transaction with additional validation."""

        if not user_id:
            print("❌ Invalid transaction detected! Reason: User ID is missing or invalid.")
            return False

        if amount <= 0:
            print("❌ Invalid transaction detected! Reason: Amount must be greater than 0.")
            return False

        if amount < 1.00:
            print("❌ Invalid transaction detected! Reason: Amount must be at least $1.00.")
            return False

        if not isinstance(payment_method, PaymentMethod):
            print("❌ Invalid transaction detected! Reason: Invalid payment method provided.")
            return False

        print(f"Processing mock payment for User {user_id}: ${amount} via {payment_method.value}")

        # Simulate an 80% success rate for transactions
        payment_success = random.random() < 0.8

        if payment_success:
            print("✅ Payment successful!")
        else:
            print("❌ Payment failed due to a random decline.")

        return payment_success
