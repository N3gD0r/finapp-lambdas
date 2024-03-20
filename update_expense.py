from expenses_entities import Expense
from expenses_persistence import ExpenseRepositoryImplementation as Repository
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
            host=rds_host,
            db_port=int(db_port),
            user=name,
            password=password,
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
        return {
            'error': 'Internal server error'
        }
    finally:
        repo.__del__()

    return {
        'updated': updated
    }

