import jwt
import datetime
from django.conf import settings
from django.core.exceptions import PermissionDenied

def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        'iat': datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload,settings.SECRET_KEY, algorithm='HS256')
    return token

def validate_jwt(token):
    try: 
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise PermissionDenied('Token has expired')
    except jwt.InvalidTokenError as e:
        raise PermissionDenied('Invalid token: ' + str(e))