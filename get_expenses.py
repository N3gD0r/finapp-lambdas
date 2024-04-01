from load_secrets import get_secrets
from expenses_persistence import ExpenseRepositoryImplementation as Repository
from pymysql import MySQLError

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

    token = event['Authorization'].split(' ')[1]
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
    user_id = token_data.get('user_id')

    try:
        repo = Repository(
            host=db_host,
            user=db_user,
            password=db_password,
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
            'expenses': []
        }

    expenses = [expense.get_dict() for expense in records]

    for expense in expenses:
        for key in expense.keys():
            if isinstance(expense[key], datetime.datetime):
                expense[key] = expense[key].strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(expense[key], datetime.date):
                expense[key] = expense[key].strftime('%Y-%m-%d')

    return {
        'expenses': expenses
    }

