import os
import json
import boto3
from botocore.exceptions import ClientError

cognito = boto3.client("cognito-idp")
USER_POOL_ID = os.environ.get("USER_POOL_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")

def post_signup_api(event):
    body = _get_body(event)
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return _response(400, {"message": "email and password required"})

    try:
        resp = cognito.sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[{"Name": "email", "Value": email}]
        )

        try:
            cognito.admin_confirm_sign_up(UserPoolId=USER_POOL_ID, Username=email)
        except ClientError:
            pass

        return _response(201, {"message": "user signed up", "result": resp})
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
