from expenses_entities import Expense
from expenses_persistence import ExpenseRepositoryImplementation as Repository
from pymysql import MySQLError

import os


def handler(event, context):
    rds_host = os.environ['RDS_HOST']
    name = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    db_port = os.environ['RDS_PORT']

    body: dict = event['expense']
    id = event['pathParameters']['id']

    entity = Expense(
        expense_name=body['expense_name'],
        expense_amount=body['expense_amount'],
        month_year=body['month_year'],
        exp_category_id=body['exp_category_id']
    )

    try:
        updated = Repository(
            host=rds_host,
            db_port=int(db_port),
            user=name,
            password=password,
            db_name=db_name
        ).update(int(id), entity)
    except MySQLError:
        return {
            'error': 'Internal server error'
        }

    return {
        'updated': updated
    }

