import json
import os
import boto3
from botocore.exceptions import ClientError

cognito = boto3.client("cognito-idp")

USER_POOL_ID = os.environ.get("USER_POOL_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")


def lambda_handler(event, context):
    # simple router based on path + method
    path = event.get("path", "")
    method = event.get("httpMethod", "").upper()

    try:
        if path == "/signup" and method == "POST":
            return signup(event)
        if path == "/login" and method == "POST":
            return login(event)
        if path == "/forgot-password" and method == "POST":
            return forgot_password(event)
        if path == "/confirm-forgot-password" and method == "POST":
            return confirm_forgot_password(event)

        return _response(404, {"message": "Not Found"})
    except Exception as e:
        return _response(500, {"error": str(e)})


def signup(event):
    body = _get_body(event)
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return _response(400, {"message": "email and password required"})

    try:
        # Use sign_up (client) so the password is set as provided.
        resp = cognito.sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[{"Name": "email", "Value": email}]
        )

        # Confirm the user immediately (for this example). In production,
        # prefer email verification flow or use AdminCreateUser for temporary password.
        try:
            cognito.admin_confirm_sign_up(UserPoolId=USER_POOL_ID, Username=email)
        except ClientError:
            # ignore if cannot confirm
            pass

        return _response(201, {"message": "user signed up", "result": resp})

    except ClientError as e:
        return _response(400, {"error": e.response.get('Error', {}).get('Message', str(e))})


def login(event):
    body = _get_body(event)
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return _response(400, {"message": "email and password required"})

    try:
        resp = cognito.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow="ADMIN_NO_SRP_AUTH",
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password
            }
        )

        auth = resp.get("AuthenticationResult") or {}
        return _response(200, {"authentication": auth})

    except ClientError as e:
        return _response(401, {"error": e.response.get('Error', {}).get('Message', str(e))})


def forgot_password(event):
    body = _get_body(event)
    email = body.get("email")

    if not email:
        return _response(400, {"message": "email required"})

    try:
        resp = cognito.forgot_password(ClientId=CLIENT_ID, Username=email)
        return _response(200, {"message": "password reset initiated", "result": resp})
    except ClientError as e:
        return _response(400, {"error": e.response.get('Error', {}).get('Message', str(e))})


def confirm_forgot_password(event):
    body = _get_body(event)
    email = body.get("email")
    confirmation_code = body.get("confirmation_code")
    new_password = body.get("new_password")

    if not (email and confirmation_code and new_password):
        return _response(400, {"message": "email, confirmation_code, new_password required"})

    try:
        resp = cognito.confirm_forgot_password(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=confirmation_code,
            Password=new_password
        )
        return _response(200, {"message": "password changed", "result": resp})
    except ClientError as e:
        return _response(400, {"error": e.response.get('Error', {}).get('Message', str(e))})


# helpers
def _get_body(event):
    if event.get("body"):
        try:
            return json.loads(event["body"])
        except Exception:
            return {}
    return {}


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }