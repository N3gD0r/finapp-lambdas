from expenses_entities import User
from expenses_persistence import UserRepositoryImplementation as Repository
from pymysql import MySQLError

import bcrypt
import datetime
import jwt
import os


def handler(event, context):
    rds_host = os.environ['RDS_HOST']
    name = os.environ['RDS_USERNAME']
    db_port = os.environ['RDS_PORT']
    db_name = os.environ['RDS_DB_NAME']
    password = os.environ['RDS_PASSWORD']
    secret_key = os.environ['SECRET_KEY']

    username = event['username']
    user_passwd = event['password'].encode('utf-8')

    try:
        check_user = Repository(
            db_name=db_name,
            db_port=int(db_port),
            host=rds_host,
            password=password,
            user=name
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
        'username': username,
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
    }

    token = jwt.encode(payload=payload, key=secret_key, algorithm='HS256')

    return {
        'Authorization': f'Bearer {token}',
        'authenticated': True
    }

