import requests

API_URL = "https://c14ef56cfk.execute-api.us-east-1.amazonaws.com/Stage/signup"
EMAIL = "boopathy1@yopmail.com"
PASSWORD = "YourSecureP@ss1"

def signup(email: str, password: str):
    payload = {
        "email": email,
        "password": password
    }
    response = requests.post(API_URL, json=payload)
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:", response.json())
    except ValueError:
        print("Response Text:", response.text)

if __name__ == "__main__":
    signup(EMAIL, PASSWORD)
