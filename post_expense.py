from load_secrets import get_env
from expenses_entities import Expense
from expenses_persistence import ExpenseRepositoryImplementation as Repository
from pymysql import MySQLError

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

    token = event['Authorization'].split(' ')[1]
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
    user_id = token_data.get('user_id')

    body: dict = event['expense']

    entity = Expense(
        expense_name=body['expense_name'],
        expense_amount=body['expense_amount'],
        month_year=body['month_year'],
        exp_category_id=body['exp_category_id'],
        user_id=user_id
    )

    try:
        expense_id = Repository(
            host=db_host,
            db_port=int(db_port),
            user=db_user,
            password=db_password,
            db_name=db_name
        ).add(entity)
    except MySQLError:
        return {
            'error': 'Internal server error'
        }

    return {
        'expense_id': expense_id
    }

