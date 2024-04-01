from db_auth import get_credentials
from expenses_entities import ChatHistory
from expenses_persistence import ChatHistoryRepositoryImplementation as Repository
from pymysql import MySQLError

import datetime
import jwt
import os


class ChatDto:
    def __init__(self, chat: ChatHistory):
        self.content = chat.chat_message
        self.role = chat.role

    def get_dict(self):
        return {
            'content': self.content,
            'role': self.role
        }


def handler(event, context):
    rds_host = os.environ['RDS_HOST']
    db_name = os.environ['RDS_DB_NAME']
    db_port = os.environ['RDS_PORT']
    secret_key = os.environ['SECRET_KEY']
    secret_name = os.environ['SECRETS_NAME']
    creds = get_credentials(secret_name)

    token = event['Authorization'].split(' ')[1]

    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])

    user_id = token_data.get('user_id')

    try:
        repo = Repository(
            host=rds_host,
            user=creds['username'],
            password=creds['password'],
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

    chats = [ChatDto(chat).get_dict() for chat in records]

    return {
        'chats': chats
    }

