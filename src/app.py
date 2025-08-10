import json
from routes import ROUTES

def lambda_handler(event, context):
    path = event.get("path", "")
    method = event.get("httpMethod", "").upper()

    try:
        handler = ROUTES.get(method, {}).get(path)
        if handler:
            return handler(event)
        else:
            return _response(404, {"message": "Not Found"})
    except Exception as e:
        return _response(500, {"error": str(e)})


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
