from expenses_persistence import ChatHistoryRepositoryImplementation as Repository
from expenses_entities import ChatHistory
from load_secrets import get_secrets
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
    token_data = jwt.decode(jwt=token, key=secret_key, algorithms=['HS256'])
    user_id = token_data.get('user_id')

    try:
        repo = Repository(
            host=db_host,
            db_port=int(db_port),
            user=db_user,
            password=db_password,
            db_name=db_name
        )

        chats_by_user: list[ChatHistory] = repo.get_by(user_id=user_id)
        chats_by_user = [chat.chat_id for chat in chats_by_user]

        if not chats_by_user:
            return {
                'deleted': False
            }

        if len(chats_by_user) < 1:
            return {
                'deleted': False
            }
        deleted = repo.delete_batch(chat_ids=chats_by_user)
    except MySQLError:
        raise Exception('Internal server error')
    finally:
        repo.__del__()

    return {
        'deleted': deleted
    }

