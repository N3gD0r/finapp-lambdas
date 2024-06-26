from load_secrets import get_env
from expenses_entities import Expense
from expenses_persistence import ExpenseRepositoryImplementation as Repository
from pymysql import MySQLError

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

    id = event['pathParameters']['id']
    token = event['Authorization'].split(' ')[1]
    token_data = jwt.decode(jwt=token, key=secret_key, algorithms=['HS256'])
    user_id = token_data.get('user_id')

    try:
        repo = Repository(
            host=db_host,
            user=db_user,
            password=db_password,
            db_port=int(db_port),
            db_name=db_name
        )
        record = repo.get_by(user_id=user_id, expense_id=id)

        if record is None:
            raise Exception(f'Entity with id {id} not found')
        if len(record) > 1:
            raise Exception(f'More than one entity with id {id} found')
    except MySQLError:
        raise Exception('Internal server error')
    finally:
        repo.__del__()

    expense: Expense = record[0].get_dict()

    for key in expense.keys():
        if isinstance(expense[key], datetime.datetime):
            expense[key] = expense[key].strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(expense[key], datetime.date):
            expense[key] = expense[key].strftime('%Y-%m-%d')

    return {
        'expense': expense
    }

