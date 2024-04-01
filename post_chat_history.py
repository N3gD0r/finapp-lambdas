from load_secrets import get_secrets
from expenses_entities import ChatHistory
from expenses_persistence import ChatHistoryRepositoryImplementation as Repository
from pymysql import MySQLError

import jwt
import os


def handler(event, context):
    secret_name = os.environ['SECRETS_NAME']
    secrets = get_secrets(secret_name)
    db_name = 'chats'
    db_host = secrets.get('db_host')
    db_port = secrets.get('db_port')
    db_user = secrets.get('username')
    db_password = secrets.get('password')
    secret_key = secrets.get('jwt_key')

    token = event['Authorization'].split(' ')[1]
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
    user_id = token_data.get('user_id')
    body: dict = event['chats']

    chats: list[ChatHistory] = [ChatHistory(user_id=user_id, **chat) for chat in body['chats']]

    try:
        repo = Repository(
            host=db_host,
            db_port=int(db_port),
            user=db_user,
            password=db_password,
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

