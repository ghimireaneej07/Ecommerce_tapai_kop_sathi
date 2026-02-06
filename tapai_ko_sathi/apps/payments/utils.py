import urllib.parse
import urllib.request

from django.conf import settings


def verify_esewa_transaction(order_number: str, amount: float, ref_id: str) -> bool:
    """
    Server-side verification of eSewa transaction.

    eSewa provides a transaction record endpoint where we submit:
    amt, scd (merchant code), pid (order id), rid (reference id).
    If the response contains 'Success', we treat it as a valid payment.
    """
    merchant_code = settings.ESEWA_MERCHANT_CODE
    if not merchant_code:
        # In case merchant code is not configured, fail closed to avoid fake confirmations.
        return False

    params = {
        "amt": str(amount),
        "scd": merchant_code,
        "pid": order_number,
        "rid": ref_id,
    }
    url = (
        "https://uat.esewa.com.np/epay/transrec?"  # UAT/test endpoint
        + urllib.parse.urlencode(params)
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            body = response.read().decode("utf-8")
    except Exception:
        return False

    return "Success" in body

