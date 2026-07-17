"""
Payment services - Dummy payment processor for MVP.
"""


class DummyPaymentProcessor:
    """Simple dummy payment processor for MVP. Replace with Stripe/PayPal in production."""
    
    @staticmethod
    def process_payment(amount, payment_method='credit_card'):
        """Process payment and return result."""
        # In production, integrate with Stripe, PayPal, or other payment gateway
        # For MVP, always return success
        import uuid
        return {
            'success': True,
            'transaction_id': f'DUMMY-{uuid.uuid4().hex[:8].upper()}',
            'amount': amount,
            'payment_method': payment_method,
            'message': 'Payment processed successfully (dummy processor)'
        }
    
    @staticmethod
    def validate_payment_method(payment_method):
        """Validate payment method."""
        valid_methods = ['credit_card', 'debit_card', 'wallet']
        return payment_method in valid_methods
    
    @staticmethod
    def refund_payment(transaction_id, amount):
        """Refund a payment."""
        return {
            'success': True,
            'refund_transaction_id': f'REFUND-{transaction_id}',
            'amount': amount
        }
