from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer as Serializer

class User(UserMixin):
    def __init__(self, email, password=None, reset_token=None):
        self.email = email
        self.password = generate_password_hash(password) if password else None
        self.reset_token = reset_token

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.email}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token)['user_id']
        except:
            return None
        return email

class Contact:
    def __init__(self, mobile, email, address, reg_number):
        self.mobile = mobile
        self.email = email
        self.address = address
        self.reg_number = reg_number
        self.created_at = datetime.utcnow()
