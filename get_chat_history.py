from expenses_entities import ChatHistory
from expenses_persistence import ChatHistoryRepositoryImplementation as Repository
from pymysql import MySQLError

import datetime
import jwt
import os


def handler(event, context):
    rds_host = os.environ['RDS_HOST']
    name = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    db_port = os.environ['RDS_PORT']
    secret_key = os.environ['SECRET_KEY']

    token = event['Authorization'].split(' ')[1]

    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])

    user_id = token_data.get('user_id')

    try:
        repo = Repository(
            host=rds_host,
            user=name,
            password=password,
            db_port=int(db_port),
            db_name=db_name
        )
        records = repo.get_by(user_id=user_id)
    except MySQLError:
        raise Exception('Internal server error')
    finally:
        repo.__del__()

    if records is None:
        return {
            'chats': []
        }

    chats = [chat.get_dict() for chat in records]

    for chat in chats:
        for key in chat.keys():
            if isinstance(chat[key], datetime.datetime):
                chat[key] = chat[key].strftime('%Y-%m-%d %H:%M:%S')

    return {
        'chats': chats
    }

