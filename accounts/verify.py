import random
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from django.conf import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
verify = client.verify

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(phone_number, otp):
    try:
        verification = client.verify.v2.services(
        settings.TWILIO_VERIFY_SID
    ).verifications.create(to=phone_number, channel="sms")
        return verification.sid
    except TwilioException as e:
        print("Error sending OTP:", e)
        return None

def check_otp(phone, code):
    try:
        verification_check = client.verify.v2.services(
        settings.TWILIO_VERIFY_SID
    ).verification_checks.create(to=phone, code=code)
        return verification_check.status == "approved"
    except TwilioException as e:
        print("Error checking OTP:", e)
        return False
