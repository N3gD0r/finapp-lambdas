from db_auth import get_credentials
from expenses_entities import User
from expenses_persistence import UserRepositoryImplementation
from pymysql import MySQLError

import bcrypt
import datetime
import jwt
import os


def handler(event, context):
    rds_host = os.environ['RDS_HOST']
    db_name = os.environ['RDS_DB_NAME']
    db_port = os.environ['RDS_PORT']
    secret_key = os.environ['SECRET_KEY']
    secret_name = os.environ['SECRETS_NAME']
    creds = get_credentials(secret_name)

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
            host=rds_host,
            db_port=int(db_port),
            db_name=db_name,
            user=creds['username'],
            password=creds['password']
        ).add(entity=user)
    except MySQLError:
        return {
            'error': 'Internal server error',
        }

    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
    }

    token = jwt.encode(payload=payload, algorithm='HS256', key=secret_key)

    return {
        'Authorization': f'Bearer {token}'
    }

