from load_secrets import get_secrets
from expenses_entities import Expense
from expenses_persistence import ExpenseRepositoryImplementation as Repository
from pymysql import MySQLError

import jwt
import os


def handler(event, context):
    secret_name = os.environ['SECRETS_NAME']
    secrets = get_secrets(secret_name)
    db_name = "expenses"
    db_host = secrets.get('db_host')
    db_port = secrets.get('db_port')
    db_user = secrets.get('username')
    db_password = secrets.get('password')
    secret_key = secrets.get('jwt_key')

    body: dict = event['expense']
    id = event['pathParameters']['id']
    token = event['Authorization'].split(' ')[1]
    token_data = jwt.decode(jwt=token, key=secret_key, algorithms=['HS256'])
    user_id = token_data.get('user_id')

    entity = Expense(
        expense_name=body['expense_name'],
        expense_amount=body['expense_amount'],
        month_year=body['month_year'],
        exp_category_id=body['exp_category_id'],
        user_id=user_id
    )

    try:
        repo = Repository(
            host=db_host,
            db_port=int(db_port),
            user=db_user,
            password=db_password,
            db_name=db_name
        )
        expense_by_user = repo.get_by(user_id=user_id, expense_id=id)

        if not expense_by_user:
            return {
                'updated': False
            }

        if len(expense_by_user) > 1:
            return {
                'updated': False
            }

        updated = repo.update(int(id), entity)
    except MySQLError:
        raise Exception('Internal server error')
    finally:
        repo.__del__()

    return {
        'updated': updated
    }

