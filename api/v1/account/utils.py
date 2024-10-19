import datetime
import jwt
from django.conf import settings 
from dateutil import parser
from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
from nexblooms.settings import EMAIL_HOST_USER
import re

# *************************************
# JWT Token Generation Functions
# *************************************


def generate_access_token(user):

    access_token_payload = {'user_id': user, 'token_type': 'access', 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1), 'jti': "b932ba39d8024b39a55b3850129cbd10"}

    return jwt.encode(access_token_payload,settings.SECRET_KEY, algorithm='HS256')


def generate_refresh_token(user):
    refresh_token_payload = {'user_id': user, 'token_type': 'refresh', 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7), 'jti': "b932ba39d8024b39a55b3850129cbd10"}

    return jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')


def get_access_tokens_for_user(user, remember_me):
    """
    Generates an access token for the user.

    Parameters:
    - user: The user ID to include in the token.
    - remember_me: Boolean indicating whether to extend token validity.

    Returns:
    - A JWT access token.
    """
    if remember_me:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    else:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=4)

    access_token_payload = {
        'user_id': user,
        'token_type': 'access',
        'exp': exp_time,
        'jti': "b932ba39d8024b39a55b3850129cbd10"
    }
    return jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')

def get_refresh_tokens_for_user(user, remember_me):
    """
    Generates a refresh token for the user.

    Parameters:
    - user: The user ID to include in the token.
    - remember_me: Boolean indicating whether to extend token validity.

    Returns:
    - A JWT refresh token.
    """
    if remember_me:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=500)
    else:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=4)

    refresh_token_payload = {
        'user_id': user,
        'token_type': 'refresh',
        'exp': exp_time,
        'jti': "b932ba39d8024b39a55b3850129cbd10"
    }
    return jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')

def get_app_access_tokens_for_user(user, remember_me):
    """
    Generates an access token specific to the app.

    Parameters:
    - user: The user ID to include in the token.
    - remember_me: Boolean indicating whether to extend token validity.

    Returns:
    - A JWT access token.
    """
    if remember_me:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    else:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)

    access_token_payload = {
        'user_id': user,
        'token_type': 'access',
        'exp': exp_time,
        'jti': "b932ba39d8024b39a55b3850129cbd10"
    }
    return jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')

def get_app_refresh_tokens_for_user(user, remember_me):
    """
    Generates a refresh token specific to the app.

    Parameters:
    - user: The user ID to include in the token.
    - remember_me: Boolean indicating whether to extend token validity.

    Returns:
    - A JWT refresh token.
    """
    if remember_me:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
    else:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=4)

    refresh_token_payload = {
        'user_id': user,
        'token_type': 'refresh',
        'exp': exp_time,
        'jti': "b932ba39d8024b39a55b3850129cbd10"
    }
    return jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')

def get_web_access_tokens_for_user(user, remember_me):
    """
    Generates an access token specific to the web.

    Parameters:
    - user: The user ID to include in the token.
    - remember_me: Boolean indicating whether to extend token validity.

    Returns:
    - A JWT access token.
    """
    if remember_me:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    else:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)

    access_token_payload = {
        'user_id': user,
        'token_type': 'access',
        'exp': exp_time,
        'jti': "b932ba39d8024b39a55b3850129cbd10"
    }
    return jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')

def get_web_refresh_tokens_for_user(user, remember_me):
    """
    Generates a refresh token specific to the web.

    Parameters:
    - user: The user ID to include in the token.
    - remember_me: Boolean indicating whether to extend token validity.

    Returns:
    - A JWT refresh token.
    """
    if remember_me:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
    else:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=4)

    refresh_token_payload = {
        'user_id': user,
        'token_type': 'refresh',
        'exp': exp_time,
        'jti': "b932ba39d8024b39a55b3850129cbd10"
    }
    return jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')

# *************************************
# OTP Generation Functions
# *************************************

def generate_otp_for_email():
    """
    Generates a One-Time Password (OTP) for email verification.

    Returns:
    - A string representing the OTP.
    """
    # otp = get_random_string(4, allowed_chars='0123456789')
    otp = "1111"
    return otp

def generate_otp_for_mobile():
    """
    Generates a One-Time Password (OTP) for mobile verification.

    Returns:
    - A string representing the OTP.
    """
    # otp = get_random_string(4, allowed_chars='0123456789')
    otp = "1111"
    return otp

# *************************************
# OTP Time Calculation Functions
# *************************************

def otp_time_generate(user_object):
    """
    Calculates the time difference between the current time and the last OTP generation time for mobile.

    Parameters:
    - user_object: The user object containing the OTP generation time.

    Returns:
    - The difference in minutes between the current time and the OTP generation time.
    """
    current_otp_time = str(datetime.datetime.now())
    otp_time = str(user_object.mobile_otp_generate_time) if user_object.mobile_otp_generate_time else None
    fmt = '%Y-%m-%d %H:%M:%S'

    if otp_time is None:
        return 25

    d1 = datetime.datetime.strptime(str(otp_time.split(".")[0]), fmt)
    d2 = datetime.datetime.strptime(str(current_otp_time.split(".")[0]), fmt)
    daysDiff = (d2 - d1)
    minutesDiff = int(daysDiff.total_seconds() / 60)
    return minutesDiff

def otp_email_time_generate(user_object):
    """
    Calculates the time difference between the current time and the last OTP generation time for email.

    Parameters:
    - user_object: The user object containing the OTP generation time.

    Returns:
    - The difference in minutes between the current time and the OTP generation time.
    """
    current_otp_time = str(datetime.datetime.now())
    otp_time = str(user_object.email_otp_generate_time) if user_object.email_otp_generate_time else None
    fmt = '%Y-%m-%d %H:%M:%S'

    if otp_time is None:
        return 25

    d1 = datetime.datetime.strptime(str(otp_time.split(".")[0]), fmt)
    d2 = datetime.datetime.strptime(str(current_otp_time.split(".")[0]), fmt)
    daysDiff = (d2 - d1)
    minutesDiff = int(daysDiff.total_seconds() / 60)
    return minutesDiff

def otp_mobile_time_generate(user_object):
    """
    Calculates the time difference between the current time and the last OTP generation time for mobile.

    Parameters:
    - user_object: The user object containing the OTP generation time.

    Returns:
    - The difference in minutes between the current time and the OTP generation time.
    """
    current_otp_time = str(datetime.datetime.now())
    otp_time = str(user_object.mobile_otp_generate_time) if user_object.mobile_otp_generate_time else None
    fmt = '%Y-%m-%d %H:%M:%S'

    if otp_time is None:
        return 25

    d1 = datetime.datetime.strptime(str(otp_time.split(".")[0]), fmt)
    d2 = datetime.datetime.strptime(str(current_otp_time.split(".")[0]), fmt)
    daysDiff = (d2 - d1)
    minutesDiff = int(daysDiff.total_seconds() / 60)
    return minutesDiff

# *************************************
# Email Utility Functions
# *************************************

def forget_password_mail(subject, recipient_list, cc_email, html_message):
    """
    Sends a reset password email.

    Parameters:
    - subject: The subject of the email.
    - recipient_list: List of recipient email addresses.
    - cc_email: List of CC email addresses.
    - html_message: The HTML content of the email.

    Returns:
    - None
    """
    email_from = EMAIL_HOST_USER
    reset_email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=email_from,
        to=recipient_list,
        cc=cc_email,
        reply_to=cc_email,
    )
    reset_email.content_subtype = "html"
    reset_email.send(fail_silently=True)

# *************************************
# Password Reset Token Functions
# *************************************

def reset_password_access_token(user):
    """
    Generates an access token for resetting the password.

    Parameters:
    - user: The user object.

    Returns:
    - A JWT access token.
    """
    expayer_time = 50000
    access_token_payload = {
        'user_id': user.username,
        "username": user.email,
        'password': user.password,
        'token_type': 'access',
        'exp': datetime.datetime.now() + datetime.timedelta(seconds=expayer_time),
        'expt': str(datetime.datetime.now() + datetime.timedelta(seconds=expayer_time)),
        'jti': "b932ba39d8024b39a55b3850129cbd10"
    }
    return jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')

def decode_reset_password_access_token(token):
    """
    Decodes the reset password access token and validates its expiration.

    Parameters:
    - token: The JWT token to decode.

    Returns:
    - A tuple containing a boolean indicating validity, the username, and the password.
    """
    now_datetime = datetime.datetime.now()
    payload = None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        time_parsed = parser.parse(payload['expt'])
    except jwt.ExpiredSignatureError:
        print("Expired signature")
    if payload and now_datetime < time_parsed:
        return True, payload['username'], payload['password']
    else:
        return False

# *************************************
# Password Validation Functions
# *************************************

def passwordValidate(password, con_password):
    """
    Validates the given password against the defined criteria.

    Parameters:
    - password: The password to validate.
    - con_password: The confirmation password to validate.

    Returns:
    - A tuple containing a boolean indicating validity and a message.
    """
    password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{5,20}$'
    if (not re.match(password_pattern, password)) or (not re.match(password_pattern, con_password)):
        return False, "Password must be between 5-20 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character."
    else:
        return True, "Password"
