from expenses_persistence import ExpenseRepositoryImplementation as Repository
from pymysql import MySQLError

import datetime
import jwt
import os


def handler(event, context):
    rds_host = os.environ['RDS_HOST']
    name = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    db_port = os.environ['RDS_PORT']
    secret_key = os.environ['SECRET_KEY']

    id = event['pathParameters']['id']

    token = event['Authorization'].split(' ')[1]
    

    try:
        record = Repository(
            host=rds_host,
            user=name,
            password=password,
            db_port=int(db_port),
            db_name=db_name
        ).get(int(id))
    except MySQLError:
        return {
            'error': 'Internal server error'
        }

    if record is None:
        raise Exception(f'Entity with id {id} not found')

    expense = record.get_dict()

    for key in expense.keys():
        if isinstance(expense[key], datetime.datetime):
            expense[key] = expense[key].strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(expense[key], datetime.date):
            expense[key] = expense[key].strftime('%Y-%m-%d')

    return {
        'expense': expense
    }

