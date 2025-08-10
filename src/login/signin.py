import os
import json
import boto3
from botocore.exceptions import ClientError

cognito = boto3.client("cognito-idp")
USER_POOL_ID = os.environ.get("USER_POOL_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")

def post_login_api(event):
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
