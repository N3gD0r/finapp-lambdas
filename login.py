from load_secrets import get_secrets
from expenses_entities import User
from expenses_persistence import UserRepositoryImplementation as Repository
from pymysql import MySQLError

import bcrypt
import datetime
import jwt
import os


def handler(event, context):
    secret_name = os.environ['SECRETS_NAME']
    secrets = get_secrets(secret_name)
    db_name = 'expenses'
    db_host = secrets.get('db_host')
    db_port = secrets.get('db_port')
    db_user = secrets.get('username')
    db_password = secrets.get('password')
    secret_key = secrets.get('jwt_key')

    username = event['username']
    user_passwd = event['password'].encode('utf-8')

    try:
        check_user = Repository(
            db_name=db_name,
            db_port=int(db_port),
            host=db_host,
            password=db_password,
            user=db_user
        ).get_by(username=username)
    except MySQLError:
        return {
            'error': 'Internal server error',
        }

    if check_user is None or len(check_user) == 0:
        return {
            'error': 'Incorrect credentials',
            'authenticated': False
        }

    user: User = check_user[0]

    matches = bcrypt.checkpw(password=user_passwd, hashed_password=user.password.encode('utf-8'))

    if not matches:
        return {
            'error': 'Incorrect credentials',
            'authenticated': False
        }

    payload = {
        'user_id': user.user_id,
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
    }

    token = jwt.encode(payload=payload, key=secret_key, algorithm='HS256')

    return {
        'Authorization': f'Bearer {token}',
        'authenticated': True
    }

