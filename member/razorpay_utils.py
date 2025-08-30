from django.conf import settings

def get_client():
    # Lazy import → no import errors during manage.py commands
    import razorpay
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
