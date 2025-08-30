import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Payment, Membership
from .razorpay_utils import get_client

logger = logging.getLogger(__name__)

PRICE_RUPEES = 25
PRICE_PAISE = PRICE_RUPEES * 100


@login_required
@require_POST
def create_order(request):
    """
    Create a Razorpay order for ₹25 and return order info to frontend.
    """
    client = get_client()
    receipt = f"mem-{request.user.id}-{int(timezone.now().timestamp())}"

    try:
        order = client.order.create({
            "amount": PRICE_PAISE,
            "currency": "INR",
            "receipt": receipt,
            "payment_capture": 1,
            "notes": {"user_id": request.user.id, "type": "membership_25_month"},
        })
    except Exception as e:
        logger.exception("Razorpay order creation failed")
        return JsonResponse({"error": "Unable to create order"}, status=500)

    Payment.objects.create(
        user=request.user,
        amount=PRICE_PAISE,
        currency="INR",
        order_id=order["id"],
        receipt=receipt,
        notes=order.get("notes") or {},
        status="created",
    )

    return JsonResponse({
        "order_id": order["id"],
        "amount": PRICE_PAISE,
        "currency": "INR",
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,  # safe to expose
    })


@login_required
@require_POST
def verify_checkout_signature(request):
    """
    Verify Razorpay payment signature (fallback for instant activation).
    """
    from razorpay import Utility, errors

    order_id = request.POST.get("razorpay_order_id")
    payment_id = request.POST.get("razorpay_payment_id")
    signature = request.POST.get("razorpay_signature")

    if not (order_id and payment_id and signature):
        return HttpResponseBadRequest("Missing fields")

    try:
        Utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
    except errors.SignatureVerificationError:
        logger.warning("Signature verification failed for order %s", order_id)
        return HttpResponseBadRequest("Invalid payment signature")

    try:
        with transaction.atomic():
            p = Payment.objects.select_for_update().select_related("user").get(order_id=order_id)

            if p.status != "paid":
                p.status = "paid"
                p.payment_id = payment_id
                p.signature = signature
                p.extra_data = request.POST.dict()  # optional JSONField in model
                p.save(update_fields=["status", "payment_id", "signature", "extra_data"])

                # Ensure membership record exists
                membership, _ = Membership.objects.get_or_create(user=p.user)
                membership.extend_30_days(from_now=False)

                logger.info("Membership extended for user %s via payment %s", p.user.id, payment_id)
            else:
                logger.info("Duplicate verification attempt for order %s", order_id)

    except Payment.DoesNotExist:
        logger.error("Payment record not found for order %s", order_id)
        return HttpResponseBadRequest("Payment not found")

    return JsonResponse({"ok": True})
