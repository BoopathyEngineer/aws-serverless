import os
import json
import boto3
from botocore.exceptions import ClientError

cognito = boto3.client("cognito-idp")
CLIENT_ID = os.environ.get("CLIENT_ID")

def post_forgot_password_api(event):
    body = _get_body(event)
    email = body.get("email")

    if not email:
        return _response(400, {"message": "email required"})

    try:
        resp = cognito.forgot_password(ClientId=CLIENT_ID, Username=email)
        return _response(200, {"message": "password reset initiated", "result": resp})
    except ClientError as e:
        return _response(400, {"error": e.response.get('Error', {}).get('Message', str(e))})

def post_confirm_forgot_password_api(event):
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
