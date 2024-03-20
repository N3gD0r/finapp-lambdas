from expenses_entities import ChatHistory
from expenses_persistence import ChatHistoryRepositoryImplementation as Repository
from pymysql import MySQLError

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
    body: dict = event['chat_history']

    chat_history = ChatHistory(
        chat_message=body['chat_message'],
        user_id=user_id
    )

    try:
        repo = Repository(
            host=rds_host,
            db_port=int(db_port),
            user=name,
            password=password,
            db_name=db_name
        )
        chat_id = repo.add(chat_history)
    except MySQLError:
        raise Exception('Internal server error')
    finally:
        repo.__del__()

    return {
        'chat_id': chat_id
    }

