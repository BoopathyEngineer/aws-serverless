from login.signup import post_signup_api
from login.signin import post_login_api
from login.forgot_password import post_forgot_password_api, post_confirm_forgot_password_api

ROUTES = {
    'POST': {
        '/signup': post_signup_api,
        '/login': post_login_api,
        '/forgot-password': post_forgot_password_api,
        '/confirm-forgot-password': post_confirm_forgot_password_api
    }
}
