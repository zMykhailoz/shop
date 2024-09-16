from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from .models import Order


@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    # Add a five seconds pause for PayPal to send IPN data
    time.sleep(5)

    # Grab the info that PayPal sends
    paypal_obj = sender
    # Grab the invoice
    my_invoice = str(paypal_obj.invoice)

    # Match the PayPal invoice the Order invoice
    # Look Up the Order
    my_order = Order.objects.get(invoice=my_invoice)

    # Record the Order was paid
    my_order.paid = True
    # Save the Order
    my_order.save()
