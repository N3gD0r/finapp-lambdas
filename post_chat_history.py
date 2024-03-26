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
    body: dict = event['chats']

    chats: list[ChatHistory] = [ChatHistory(user_id=user_id, **chat) for chat in body['chats']]

    try:
        repo = Repository(
            host=rds_host,
            db_port=int(db_port),
            user=name,
            password=password,
            db_name=db_name
        )
        rows = repo.add_batch(entities=chats)
    except MySQLError:
        raise Exception('Internal server error')
    finally:
        repo.__del__()

    return {
        'chats_added': rows
    }

