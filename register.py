from load_secrets import get_env
from expenses_entities import User
from expenses_persistence import UserRepositoryImplementation
from pymysql import MySQLError

import bcrypt
import datetime
import jwt
import os


def handler(event, context):
    secrets = get_env()
    db_name = 'expenses'
    db_host = secrets.get('db_host')
    db_port = secrets.get('db_port')
    db_user = secrets.get('username')
    db_password = secrets.get('password')
    secret_key = secrets.get('jwt_key')

    username = event['username']
    user_passwd = event['password'].encode('utf-8')

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_passwd, salt)

    user = User(
        username=username,
        password=hashed_password
    )

    try:
        user_id = UserRepositoryImplementation(
            host=db_host,
            db_port=int(db_port),
            db_name=db_name,
            user=db_user,
            password=db_password,
        ).add(entity=user)
    except MySQLError:
        return {
            'error': 'Internal server error',
        }

    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
    }

    token = jwt.encode(payload=payload, algorithm='HS256', key=secret_key)

    return {
        'Authorization': f'Bearer {token}'
    }

